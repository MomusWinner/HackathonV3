import { defineStore } from "pinia";
import type { Document, DocumentBrief } from "~/types/document"; // Adjust the import path

type WsResponse = {
	processing_status: "processing";
	ws_url: string;
};

type ProcessingResponse = WsResponse | Document;

type BriefsResponse = {
	results: DocumentBrief[];
};

export const useDocumentStore = defineStore("document", () => {
	const documents = ref<Document[]>([]);
	const documentBriefs = ref<DocumentBrief[]>([]);
	const sockets = ref<{ [key: string]: WebSocket }>({});
	const userStore = useUserStore();

	async function fetchDocument(id: string) {
		try {
			const response = await $fetch<ProcessingResponse>(
				`/api/v1/documents/${id}`,
			);

			switch (response.processing_status) {
				case "processing":
					setupWebSocketListener(id, (response as WsResponse).ws_url);
					break;
				case "completed":
					addOrUpdateDocument(response as Document);
					break;
			}
		} catch (error) {
			console.error("Error fetching document:", error);
			throw error;
		}
	}

	async function fetchDocumentBriefs() {
		const user = userStore.getUser();
		try {
			const response = await $fetch<BriefsResponse>(
				`/api/v1/documents/?user_id=${user}`,
			);

			documentBriefs.value = response.results;
		} catch (error) {
			console.error("Error fetching document:", error);
			throw error;
		}
	}

	function setupWebSocketListener(documentId: string, wsUrl: string) {
		const socket = new WebSocket(wsUrl);
		sockets.value[documentId] = socket;

		socket.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			if (data.processing_status === "completed") {
				addOrUpdateDocument(data);
				socket.close();
				delete sockets.value[documentId];
			}
		});

		socket.addEventListener("close", () => {
			delete sockets.value[documentId];
		});
	}

	function addOrUpdateDocument(document: Document) {
		const index = documents.value.findIndex((d) => d.id === document.id);
		if (index === -1) {
			documents.value.push(document);
		} else {
			documents.value[index] = document;
		}
	}

	function addOrUpdateDocumentBrief(documentBrief: DocumentBrief) {
		const index = documents.value.findIndex((d) => d.id === documentBrief.id);
		if (index === -1) {
			documentBriefs.value.push(documentBrief);
		} else {
			documentBriefs.value[index] = documentBrief;
		}
	}

	function getDocument(id: string): Document | undefined {
		return documents.value.find((d) => d.id === id);
	}

	function getBriefs(): DocumentBrief[] {
		return documentBriefs.value;
	}

	function cleanupWebSockets() {
		Object.values(sockets.value).forEach((socket) => socket.close());
		sockets.value = {};
	}

	return {
		documents,
		documentBriefs,
		fetchDocumentBriefs,
		fetchDocument,
		getDocument,
		getBriefs,
		cleanupWebSockets,
	};
});
