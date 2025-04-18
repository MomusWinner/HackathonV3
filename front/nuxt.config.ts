import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
	compatibilityDate: "2024-11-01",
	modules: ["shadcn-nuxt"],
	devtools: { enabled: true },
	css: ["~/assets/css/tailwind.css"],
	vite: {
		plugins: [tailwindcss()],
	},
	ssr: false,

	shadcn: {
		prefix: "",
		componentDir: "./components/ui",
	},
});
