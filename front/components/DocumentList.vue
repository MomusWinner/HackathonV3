<script lang="ts" setup>
import { Plus } from "lucide-vue-next";
import { useDocumentStore } from "@/stores/documents";
const documentStore = useDocumentStore();
const { current: undefined } = defineProps<{ current?: string }>();

const documents = computed(() => documentStore.getBriefs());

onMounted(async () => {
	await documentStore.fetchDocumentBriefs();
});
function goToDocument(id: string) {
	navigateTo(`/document/${id}`);
}
function goToMain() {
	navigateTo("/");
}
</script>

<template>
	<div class="flex flex-col gap-3 bg-primary/3 p-2 rounded-lg">
		<div class="font-medium text-lg">Документы</div>
		<div class="flex w-full flex-col gap-2">
			<Button
				@click="goToMain()"
				class="w-full px-4 py-2"
				:class="
					!current
						? 'bg-primary/15 hover:bg-primary/15'
						: 'bg-primary/7 hover:bg-primary/15'
				"
				variant="secondary"
			>
				<Plus />
			</Button>
			<div v-for="document of documents" :key="document.id" class="w-full">
				<Button
					@click="goToDocument(document.id)"
					class="w-full px-4 py-2 text-left justify-start items-start"
					:class="
						current && document.id == current
							? 'bg-primary/15 hover:bg-primary/15'
							: 'bg-primary/7 hover:bg-primary/15'
					"
					variant="secondary"
				>
					<span v-if="document.processing_status == 'completed'">
						{{
							document.title.length > 30
								? document.title.slice(0, 30) + "..."
								: document.title
						}}
					</span>
					<span v-else-if="document.processing_status == 'failed'">
						Failed :(
					</span>
					<span v-else>Processing...</span>
				</Button>
			</div>
		</div>
	</div>
</template>
