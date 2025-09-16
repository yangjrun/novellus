import { ChakraProvider, createSystem, defaultConfig } from "@chakra-ui/react"

const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        // Primary brand colors - deep blue palette for writing/creativity theme
        brand: {
          50: { value: "#e8f4fd" },
          100: { value: "#bee2f9" },
          200: { value: "#94d1f5" },
          300: { value: "#6abff1" },
          400: { value: "#40aeed" },
          500: { value: "#169ce9" },
          600: { value: "#1280ba" },
          700: { value: "#0e648b" },
          800: { value: "#0a485c" },
          900: { value: "#062c2d" }
        },
        // Secondary colors for different tool categories
        narrative: {
          50: { value: "#f0f9ff" },
          100: { value: "#e0f2fe" },
          200: { value: "#bae6fd" },
          300: { value: "#7dd3fc" },
          400: { value: "#38bdf8" },
          500: { value: "#0ea5e9" },
          600: { value: "#0284c7" },
          700: { value: "#0369a1" },
          800: { value: "#075985" },
          900: { value: "#0c4a6e" }
        },
        character: {
          50: { value: "#fefce8" },
          100: { value: "#fef9c3" },
          200: { value: "#fef08a" },
          300: { value: "#fde047" },
          400: { value: "#facc15" },
          500: { value: "#eab308" },
          600: { value: "#ca8a04" },
          700: { value: "#a16207" },
          800: { value: "#854d0e" },
          900: { value: "#713f12" }
        },
        world: {
          50: { value: "#f0fdf4" },
          100: { value: "#dcfce7" },
          200: { value: "#bbf7d0" },
          300: { value: "#86efac" },
          400: { value: "#4ade80" },
          500: { value: "#22c55e" },
          600: { value: "#16a34a" },
          700: { value: "#15803d" },
          800: { value: "#166534" },
          900: { value: "#14532d" }
        },
        scene: {
          50: { value: "#fdf4ff" },
          100: { value: "#fae8ff" },
          200: { value: "#f5d0fe" },
          300: { value: "#f0abfc" },
          400: { value: "#e879f9" },
          500: { value: "#d946ef" },
          600: { value: "#c026d3" },
          700: { value: "#a21caf" },
          800: { value: "#86198f" },
          900: { value: "#701a75" }
        }
      },
      fonts: {
        heading: { value: "'Inter', system-ui, sans-serif" },
        body: { value: "'Inter', system-ui, sans-serif" },
        mono: { value: "'JetBrains Mono', 'Fira Code', monospace" }
      },
      fontSizes: {
        "xs": { value: "0.75rem" },
        "sm": { value: "0.875rem" },
        "md": { value: "1rem" },
        "lg": { value: "1.125rem" },
        "xl": { value: "1.25rem" },
        "2xl": { value: "1.5rem" },
        "3xl": { value: "1.875rem" },
        "4xl": { value: "2.25rem" },
        "5xl": { value: "3rem" },
        "6xl": { value: "3.75rem" },
        "7xl": { value: "4.5rem" }
      },
      fontWeights: {
        thin: { value: "100" },
        light: { value: "300" },
        normal: { value: "400" },
        medium: { value: "500" },
        semibold: { value: "600" },
        bold: { value: "700" },
        extrabold: { value: "800" },
        black: { value: "900" }
      },
      lineHeights: {
        none: { value: "1" },
        tight: { value: "1.25" },
        snug: { value: "1.375" },
        normal: { value: "1.5" },
        relaxed: { value: "1.625" },
        loose: { value: "2" }
      },
      letterSpacings: {
        tighter: { value: "-0.05em" },
        tight: { value: "-0.025em" },
        normal: { value: "0em" },
        wide: { value: "0.025em" },
        wider: { value: "0.05em" },
        widest: { value: "0.1em" }
      },
      spacing: {
        "0": { value: "0" },
        "0.5": { value: "0.125rem" },
        "1": { value: "0.25rem" },
        "1.5": { value: "0.375rem" },
        "2": { value: "0.5rem" },
        "2.5": { value: "0.625rem" },
        "3": { value: "0.75rem" },
        "3.5": { value: "0.875rem" },
        "4": { value: "1rem" },
        "5": { value: "1.25rem" },
        "6": { value: "1.5rem" },
        "7": { value: "1.75rem" },
        "8": { value: "2rem" },
        "9": { value: "2.25rem" },
        "10": { value: "2.5rem" },
        "12": { value: "3rem" },
        "14": { value: "3.5rem" },
        "16": { value: "4rem" },
        "20": { value: "5rem" },
        "24": { value: "6rem" },
        "32": { value: "8rem" },
        "xs": { value: "0.5rem" },
        "sm": { value: "0.75rem" },
        "md": { value: "1rem" },
        "lg": { value: "1.5rem" },
        "xl": { value: "2rem" },
        "2xl": { value: "3rem" }
      },
      radii: {
        none: { value: "0" },
        xs: { value: "0.125rem" },
        sm: { value: "0.25rem" },
        md: { value: "0.375rem" },
        lg: { value: "0.5rem" },
        xl: { value: "0.75rem" },
        "2xl": { value: "1rem" },
        "3xl": { value: "1.5rem" },
        full: { value: "9999px" }
      },
      shadows: {
        xs: { value: "0 1px 2px 0 rgba(0, 0, 0, 0.05)" },
        sm: { value: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)" },
        md: { value: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)" },
        lg: { value: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)" },
        xl: { value: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)" },
        "2xl": { value: "0 25px 50px -12px rgba(0, 0, 0, 0.25)" },
        inner: { value: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)" }
      }
    }
  }
})

export function Provider(props: React.PropsWithChildren) {
  return (
    <ChakraProvider value={system}>
      {props.children}
    </ChakraProvider>
  )
}