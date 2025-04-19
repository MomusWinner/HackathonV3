import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
	compatibilityDate: "2025-04-19",
	modules: ["shadcn-nuxt", "@pinia/nuxt", "@vee-validate/nuxt"],
	devtools: { enabled: true },
	css: ["~/assets/css/tailwind.css"],
	vite: {
		plugins: [tailwindcss()],
	},

	shadcn: {
		prefix: "",
		componentDir: "./components/ui",
	},
});
