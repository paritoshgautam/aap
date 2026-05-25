import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        panel: "#f7f8f4",
        moss: "#496b52",
        coral: "#c95f4a",
        cobalt: "#305f9f"
      }
    }
  },
  plugins: []
};

export default config;
