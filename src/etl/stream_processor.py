"""
Stream Processor for Real-time Novel Content Processing

Advanced streaming data processing system including:
- Real-time content ingestion and processing
- Event-driven architecture with message queues
- Sliding window processing for temporal analysis
- Backpressure handling and flow control
- Fault tolerance and recovery mechanisms
- Scalable worker pools for parallel processing
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from collections import deque, defaultdict
import weakref
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from .types import ContentType, PipelineConfig
from .text_processor import TextProcessor
from .entity_extractor import EntityExtractor
from .data_validator import DataValidator

logger = logging.getLogger(__name__)


class StreamEventType(Enum):
    """Types of streaming events."""
    CONTENT_ADDED = "content_added"
    CONTENT_UPDATED = "content_updated"
    CONTENT_DELETED = "content_deleted"
    BATCH_COMPLETE = "batch_complete"
    ERROR_OCCURRED = "error_occurred"
    PIPELINE_STATUS = "pipeline_status"


class StreamSourceType(Enum):
    """Types of streaming data sources."""
    FILE_WATCHER = "file_watcher"
    DATABASE_CDC = "database_cdc"
    MESSAGE_QUEUE = "message_queue"
    HTTP_WEBHOOK = "http_webhook"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"


@dataclass
class StreamEvent:
    """A streaming event containing content and metadata."""
    event_id: str
    event_type: StreamEventType
    content_type: ContentType
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class StreamWindow:
    """A time-based window for stream processing."""
    window_id: str
    start_time: datetime
    end_time: datetime
    events: List[StreamEvent] = field(default_factory=list)
    is_closed: bool = False
    processed: bool = False


@dataclass
class StreamMetrics:
    """Metrics for stream processing."""
    events_processed: int = 0
    events_failed: int = 0
    processing_rate: float = 0.0  # events per second
    average_latency: float = 0.0  # milliseconds
    last_processed_time: Optional[datetime] = None
    active_windows: int = 0
    backpressure_events: int = 0


class StreamBuffer:
    """Thread-safe buffer for stream events with backpressure control."""

    def __init__(self, max_size: int = 10000, high_watermark: float = 0.8):
        self.max_size = max_size
        self.high_watermark = high_watermark
        self.buffer = deque()
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self._size = 0

    async def put(self, event: StreamEvent, timeout: float = 5.0) -> bool:
        """Add event to buffer with timeout."""
        def _put():
            with self.not_full:
                if not self.not_full.wait_for(lambda: self._size < self.max_size, timeout=timeout):
                    return False
                self.buffer.append(event)
                self._size += 1
                self.not_empty.notify()
                return True

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _put)

    async def get(self, timeout: float = 1.0) -> Optional[StreamEvent]:
        """Get event from buffer with timeout."""
        def _get():
            with self.not_empty:
                if not self.not_empty.wait_for(lambda: self._size > 0, timeout=timeout):
                    return None
                event = self.buffer.popleft()
                self._size -= 1
                self.not_full.notify()
                return event

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)

    def is_high_watermark(self) -> bool:
        """Check if buffer is at high watermark."""
        with self.lock:
            return self._size >= (self.max_size * self.high_watermark)

    def size(self) -> int:
        """Get current buffer size."""
        with self.lock:
            return self._size

    def clear(self):
        """Clear the buffer."""
        with self.lock:
            self.buffer.clear()
            self._size = 0
            self.not_full.notify_all()


class WindowManager:
    """Manages time-based windows for stream processing."""

    def __init__(self, window_size: timedelta, slide_interval: timedelta):
        self.window_size = window_size
        self.slide_interval = slide_interval
        self.windows: Dict[str, StreamWindow] = {}
        self.lock = asyncio.Lock()

    async def add_event(self, event: StreamEvent) -> List[str]:
        """Add event to appropriate windows and return affected window IDs."""
        async with self.lock:
            affected_windows = []

            # Find all windows that should contain this event
            for window_id, window in self.windows.items():
                if (window.start_time <= event.timestamp < window.end_time and
                    not window.is_closed):
                    window.events.append(event)
                    affected_windows.append(window_id)

            # Create new window if needed
            current_time = datetime.now()
            window_start = self._align_to_slide_interval(event.timestamp)
            window_id = f"window_{window_start.isoformat()}"

            if window_id not in self.windows:
                window_end = window_start + self.window_size
                new_window = StreamWindow(
                    window_id=window_id,
                    start_time=window_start,
                    end_time=window_end,
                    events=[event]
                )
                self.windows[window_id] = new_window
                affected_windows.append(window_id)

            # Close expired windows
            expired_windows = []
            for window_id, window in self.windows.items():
                if current_time >= window.end_time and not window.is_closed:
                    window.is_closed = True
                    expired_windows.append(window_id)

            return affected_windows

    async def get_ready_windows(self) -> List[StreamWindow]:
        """Get windows that are ready for processing."""
        async with self.lock:
            ready_windows = []
            current_time = datetime.now()

            for window in self.windows.values():
                if (window.is_closed and not window.processed and
                    current_time >= window.end_time):
                    ready_windows.append(window)

            return ready_windows

    async def mark_window_processed(self, window_id: str):
        """Mark a window as processed."""
        async with self.lock:
            if window_id in self.windows:
                self.windows[window_id].processed = True

    async def cleanup_old_windows(self, retention_period: timedelta):
        """Remove old processed windows."""
        async with self.lock:
            cutoff_time = datetime.now() - retention_period
            to_remove = []

            for window_id, window in self.windows.items():
                if window.processed and window.end_time < cutoff_time:
                    to_remove.append(window_id)

            for window_id in to_remove:
                del self.windows[window_id]

    def _align_to_slide_interval(self, timestamp: datetime) -> datetime:
        """Align timestamp to slide interval boundary."""
        seconds = int(self.slide_interval.total_seconds())
        aligned_epoch = (int(timestamp.timestamp()) // seconds) * seconds
        return datetime.fromtimestamp(aligned_epoch)


class StreamProcessor:
    """
    Advanced stream processor for real-time novel content processing.

    Features:
    - Multiple input source support
    - Time-based windowing
    - Backpressure handling
    - Fault tolerance with retries
    - Parallel processing with worker pools
    - Real-time metrics and monitoring
    """

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()

        # Core processors
        self.text_processor = TextProcessor()
        self.entity_extractor = EntityExtractor()
        self.data_validator = DataValidator()

        # Stream management
        self.event_buffer = StreamBuffer(
            max_size=self.config.batch_size * 10,
            high_watermark=0.8
        )

        # Window management
        self.window_manager = WindowManager(
            window_size=timedelta(minutes=5),
            slide_interval=timedelta(minutes=1)
        )

        # Worker management
        self.worker_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.processing_tasks: Set[asyncio.Task] = set()

        # Stream sources and handlers
        self.stream_sources: Dict[str, Any] = {}
        self.event_handlers: Dict[StreamEventType, List[Callable]] = defaultdict(list)

        # Metrics and monitoring
        self.metrics = StreamMetrics()
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # Error handling
        self.error_queue = asyncio.Queue()
        self.dead_letter_queue = deque(maxlen=1000)

        logger.info("StreamProcessor initialized")

    async def start_stream(self,
                          content_type: ContentType,
                          source_config: Dict[str, Any],
                          callback: Callable[[Dict[str, Any], ContentType], None] = None):
        """Start streaming processing for a content type."""
        if self.is_running:
            logger.warning("Stream processor is already running")
            return

        self.is_running = True
        self.shutdown_event.clear()

        logger.info(f"Starting stream processing for {content_type.value}")

        try:
            # Start core processing tasks
            processing_task = asyncio.create_task(self._process_event_loop())
            window_task = asyncio.create_task(self._process_window_loop())
            metrics_task = asyncio.create_task(self._metrics_loop())
            error_task = asyncio.create_task(self._error_handling_loop())

            self.processing_tasks.update([processing_task, window_task, metrics_task, error_task])

            # Start source-specific ingestion
            source_type = StreamSourceType(source_config.get('type', 'custom'))
            ingestion_task = await self._start_ingestion(source_type, source_config, content_type)
            if ingestion_task:
                self.processing_tasks.add(ingestion_task)

            # Wait for shutdown
            await self.shutdown_event.wait()

        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            raise
        finally:
            await self._cleanup()

    async def _start_ingestion(self,
                              source_type: StreamSourceType,
                              source_config: Dict[str, Any],
                              content_type: ContentType) -> Optional[asyncio.Task]:
        """Start ingestion from specified source type."""
        if source_type == StreamSourceType.FILE_WATCHER:
            return asyncio.create_task(self._file_watcher_ingestion(source_config, content_type))
        elif source_type == StreamSourceType.HTTP_WEBHOOK:
            return asyncio.create_task(self._webhook_ingestion(source_config, content_type))
        elif source_type == StreamSourceType.MESSAGE_QUEUE:
            return asyncio.create_task(self._message_queue_ingestion(source_config, content_type))
        else:
            logger.warning(f"Unsupported source type: {source_type}")
            return None

    async def _file_watcher_ingestion(self, config: Dict[str, Any], content_type: ContentType):
        """Ingest events from file system changes."""
        import watchdog.observers
        import watchdog.events
        from pathlib import Path

        watch_path = Path(config.get('path', '.'))
        file_patterns = config.get('patterns', ['*.txt', '*.md'])

        class FileEventHandler(watchdog.events.FileSystemEventHandler):
            def __init__(self, processor):
                self.processor = processor

            def on_modified(self, event):
                if not event.is_directory:
                    asyncio.create_task(self._handle_file_change(event.src_path, 'modified'))

            def on_created(self, event):
                if not event.is_directory:
                    asyncio.create_task(self._handle_file_change(event.src_path, 'created'))

            async def _handle_file_change(self, file_path: str, change_type: str):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    event = StreamEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=StreamEventType.CONTENT_UPDATED if change_type == 'modified' else StreamEventType.CONTENT_ADDED,
                        content_type=content_type,
                        timestamp=datetime.now(),
                        data={'content': content, 'file_path': file_path},
                        source='file_watcher',
                        metadata={'change_type': change_type}
                    )

                    await self.processor.add_event(event)

                except Exception as e:
                    logger.error(f"Failed to process file change {file_path}: {e}")

        # Set up file watcher
        event_handler = FileEventHandler(self)
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, str(watch_path), recursive=True)
        observer.start()

        try:
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        finally:
            observer.stop()
            observer.join()

    async def _webhook_ingestion(self, config: Dict[str, Any], content_type: ContentType):
        """Ingest events from HTTP webhooks."""
        from aiohttp import web

        async def webhook_handler(request):
            try:
                data = await request.json()

                event = StreamEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=StreamEventType.CONTENT_ADDED,
                    content_type=content_type,
                    timestamp=datetime.now(),
                    data=data,
                    source='webhook',
                    metadata={'remote_addr': request.remote}
                )

                success = await self.add_event(event)
                if success:
                    return web.json_response({'status': 'accepted'})
                else:
                    return web.json_response({'status': 'buffer_full'}, status=503)

            except Exception as e:
                logger.error(f"Webhook processing failed: {e}")
                return web.json_response({'status': 'error', 'message': str(e)}, status=400)

        app = web.Application()
        app.router.add_post('/webhook', webhook_handler)

        runner = web.AppRunner(app)
        await runner.setup()

        port = config.get('port', 8080)
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()

        logger.info(f"Webhook server started on port {port}")

        try:
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        finally:
            await runner.cleanup()

    async def _message_queue_ingestion(self, config: Dict[str, Any], content_type: ContentType):
        """Ingest events from message queue (Redis/RabbitMQ simulation)."""
        # This would implement actual message queue integration
        # For now, we'll simulate with periodic polling

        queue_name = config.get('queue_name', 'novel_content')
        poll_interval = config.get('poll_interval', 1)

        while not self.shutdown_event.is_set():
            try:
                # Simulate getting message from queue
                # In real implementation, this would use Redis/RabbitMQ client
                await asyncio.sleep(poll_interval)

                # Example: simulate receiving a message
                if hasattr(self, '_simulate_message') and self._simulate_message:
                    data = self._simulate_message
                    self._simulate_message = None

                    event = StreamEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=StreamEventType.CONTENT_ADDED,
                        content_type=content_type,
                        timestamp=datetime.now(),
                        data=data,
                        source='message_queue',
                        metadata={'queue': queue_name}
                    )

                    await self.add_event(event)

            except Exception as e:
                logger.error(f"Message queue ingestion failed: {e}")
                await asyncio.sleep(poll_interval * 2)  # Back off on error

    async def add_event(self, event: StreamEvent) -> bool:
        """Add event to processing stream."""
        if self.event_buffer.is_high_watermark():
            self.metrics.backpressure_events += 1
            logger.warning("Stream buffer at high watermark, applying backpressure")

        success = await self.event_buffer.put(event, timeout=5.0)
        if not success:
            logger.error(f"Failed to add event {event.event_id} to buffer (timeout)")
            await self._handle_dropped_event(event)

        return success

    async def _process_event_loop(self):
        """Main event processing loop."""
        while not self.shutdown_event.is_set():
            try:
                event = await self.event_buffer.get(timeout=1.0)
                if event:
                    await self._process_single_event(event)

            except Exception as e:
                logger.error(f"Event processing loop error: {e}")
                await asyncio.sleep(1)

    async def _process_single_event(self, event: StreamEvent):
        """Process a single stream event."""
        start_time = time.time()

        try:
            # Add to windows
            affected_windows = await self.window_manager.add_event(event)

            # Process event data
            content = event.data.get('content', '')
            if content:
                # Text processing
                cleaned_text = await self.text_processor.clean_text(content)

                # Entity extraction
                entities = await self.entity_extractor.extract_entities(
                    cleaned_text, event.content_type
                )

                # Validation
                record = {
                    'original_id': event.event_id,
                    'content_type': event.content_type.value,
                    'original_content': content,
                    'cleaned_content': cleaned_text,
                    'entities': [entity.__dict__ for entity in entities],
                    'metadata': event.metadata,
                    'processed_at': datetime.now().isoformat(),
                    'pipeline_version': '1.0'
                }

                validation_result = await self.data_validator.validate_record(
                    record, event.content_type, entities
                )

                # Update event with processed data
                event.data.update({
                    'processed_content': cleaned_text,
                    'entities': entities,
                    'validation_result': validation_result
                })

            # Call event handlers
            for handler in self.event_handlers.get(event.event_type, []):
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")

            # Update metrics
            processing_time = (time.time() - start_time) * 1000  # milliseconds
            self.metrics.events_processed += 1
            self.metrics.last_processed_time = datetime.now()

            # Update average latency
            if self.metrics.average_latency == 0:
                self.metrics.average_latency = processing_time
            else:
                self.metrics.average_latency = (self.metrics.average_latency * 0.9 + processing_time * 0.1)

        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            self.metrics.events_failed += 1
            await self._handle_event_error(event, e)

    async def _process_window_loop(self):
        """Process completed time windows."""
        while not self.shutdown_event.is_set():
            try:
                ready_windows = await self.window_manager.get_ready_windows()

                for window in ready_windows:
                    await self._process_window(window)
                    await self.window_manager.mark_window_processed(window.window_id)

                # Cleanup old windows
                await self.window_manager.cleanup_old_windows(timedelta(hours=1))

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Window processing loop error: {e}")
                await asyncio.sleep(10)

    async def _process_window(self, window: StreamWindow):
        """Process a completed time window."""
        if not window.events:
            return

        logger.debug(f"Processing window {window.window_id} with {len(window.events)} events")

        # Aggregate window statistics
        window_stats = {
            'window_id': window.window_id,
            'start_time': window.start_time,
            'end_time': window.end_time,
            'event_count': len(window.events),
            'content_types': list(set(e.content_type.value for e in window.events)),
            'sources': list(set(e.source for e in window.events))
        }

        # Call window handlers
        for handler in self.event_handlers.get(StreamEventType.BATCH_COMPLETE, []):
            try:
                await handler(window_stats)
            except Exception as e:
                logger.error(f"Window handler failed: {e}")

        self.metrics.active_windows = len([w for w in self.window_manager.windows.values() if not w.processed])

    async def _metrics_loop(self):
        """Update processing metrics."""
        last_count = 0
        last_time = time.time()

        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Update every 30 seconds

                current_time = time.time()
                current_count = self.metrics.events_processed

                # Calculate processing rate
                time_diff = current_time - last_time
                count_diff = current_count - last_count

                if time_diff > 0:
                    self.metrics.processing_rate = count_diff / time_diff

                last_count = current_count
                last_time = current_time

                # Log metrics
                logger.info(f"Stream metrics - Processed: {self.metrics.events_processed}, "
                           f"Failed: {self.metrics.events_failed}, "
                           f"Rate: {self.metrics.processing_rate:.2f}/sec, "
                           f"Avg Latency: {self.metrics.average_latency:.2f}ms, "
                           f"Buffer: {self.event_buffer.size()}")

            except Exception as e:
                logger.error(f"Metrics loop error: {e}")

    async def _error_handling_loop(self):
        """Handle processing errors and retries."""
        while not self.shutdown_event.is_set():
            try:
                # This would implement error handling and retry logic
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error handling loop error: {e}")

    async def _handle_event_error(self, event: StreamEvent, error: Exception):
        """Handle individual event processing errors."""
        event.retry_count += 1

        if event.retry_count <= event.max_retries:
            # Retry after delay
            retry_delay = min(2 ** event.retry_count, 60)  # Exponential backoff, max 60 seconds
            logger.warning(f"Retrying event {event.event_id} in {retry_delay} seconds (attempt {event.retry_count})")

            await asyncio.sleep(retry_delay)
            await self.add_event(event)
        else:
            # Move to dead letter queue
            logger.error(f"Event {event.event_id} exceeded max retries, moving to dead letter queue")
            self.dead_letter_queue.append({
                'event': event.__dict__,
                'error': str(error),
                'timestamp': datetime.now().isoformat()
            })

    async def _handle_dropped_event(self, event: StreamEvent):
        """Handle events that couldn't be added to buffer."""
        logger.error(f"Dropping event {event.event_id} due to buffer overflow")
        self.dead_letter_queue.append({
            'event': event.__dict__,
            'error': 'Buffer overflow',
            'timestamp': datetime.now().isoformat()
        })

    def add_event_handler(self, event_type: StreamEventType, handler: Callable):
        """Add event handler for specific event types."""
        self.event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: StreamEventType, handler: Callable):
        """Remove event handler."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)

    async def stop_stream(self):
        """Stop stream processing gracefully."""
        logger.info("Stopping stream processor")
        self.is_running = False
        self.shutdown_event.set()

    async def _cleanup(self):
        """Cleanup resources."""
        # Cancel all processing tasks
        for task in self.processing_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        # Shutdown worker pool
        self.worker_pool.shutdown(wait=True)

        # Clear buffers
        self.event_buffer.clear()

        logger.info("Stream processor cleanup completed")

    def get_stream_status(self) -> Dict[str, Any]:
        """Get current stream processing status."""
        return {
            'is_running': self.is_running,
            'metrics': {
                'events_processed': self.metrics.events_processed,
                'events_failed': self.metrics.events_failed,
                'processing_rate': self.metrics.processing_rate,
                'average_latency': self.metrics.average_latency,
                'active_windows': self.metrics.active_windows,
                'backpressure_events': self.metrics.backpressure_events,
                'last_processed': self.metrics.last_processed_time.isoformat() if self.metrics.last_processed_time else None
            },
            'buffer_status': {
                'size': self.event_buffer.size(),
                'max_size': self.event_buffer.max_size,
                'high_watermark': self.event_buffer.is_high_watermark()
            },
            'dead_letter_queue_size': len(self.dead_letter_queue),
            'active_tasks': len([t for t in self.processing_tasks if not t.done()])
        }

    # Utility method for testing
    def simulate_message(self, data: Dict[str, Any]):
        """Simulate a message for testing message queue ingestion."""
        self._simulate_message = data