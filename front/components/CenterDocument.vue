<script lang="ts" setup>
import { marked } from "marked";
const { document } = defineProps<{ document: Document }>();
</script>
<template>
	<div class="flex flex-col gap-3">
		<div class="text-6xl">{{ document.title }}</div>
		<div v-if="document.theme">{{ document.theme }}</div>
		<DocumentTags v-if="document.tags" :tags="document.tags" />
		<Headered v-if="document.summary" header="Краткое содержание">
			<p
				v-html="marked(document.summary)"
				class="prose prose-stone max-w-none"
			></p>
		</Headered>

		<Headered
			v-if="document.recommendations"
			header="Рекомендации по улучшению"
		>
			<p
				v-html="marked(document.recommendations)"
				class="prose prose-stone max-w-none"
			></p>
		</Headered>
		<div class="text-2xl font-medium">Смысловые блоки</div>
		<Blocks v-if="document.blocks" :blocks="document.blocks" />
	</div>
</template>
