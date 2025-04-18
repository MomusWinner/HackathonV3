import { defineStore } from "pinia";

export const useDocumentStore = defineStore("document", () => {
	const documents = ref<[]Document>([])
	
	async function getDocument(id: string): Document {
		const document = documents.find((d) => d.id == id)
	}

	return {
		getDocument
	}
});
