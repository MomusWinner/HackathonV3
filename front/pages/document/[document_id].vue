<script lang="ts" setup>
import { useDocumentStore } from "@/stores/documents";

const route = useRoute();
const documentId = route.params.document_id;
const documentStore = useDocumentStore();

const document = computed(() => documentStore.getDocument(documentId));
onMounted(async () => {
	if (!document.value) {
		await documentStore.fetchDocument(documentId);
	}
});
</script>

<template>
	<div class="flex flex-row gap-5 p-5">
		<div class="basis-1/4 justify-items-center">
			<div>
				<DocumentList :current="documentId" />
			</div>
		</div>
		<div v-if="document" class="basis-2/4">
			<CenterDocument :document="document" />
		</div>
		<div v-else class="flex flex-col basis-2/4">
            <Skeleton class="h-[100px] w-150 m-1"/>
            <div class="flex flex-row">
                <Skeleton class="h-[40px] w-[70px] m-1"/>
                <Skeleton class="h-[40px] w-[70px] m-1"/>
                <Skeleton class="h-[40px] w-[70px] m-1"/>
            </div>
            <Skeleton class="h-[50px] w-100 m-1"/>
            <Skeleton class="h-[250px] w-full m-1"/>
            <br/>
            <Skeleton class="h-[50px] w-100 m-1"/>
            <Skeleton class="h-[250px] w-full m-1"/>
		</div>
		<!-- <div class="basis-1/4"></div> -->
	</div>
</template>
