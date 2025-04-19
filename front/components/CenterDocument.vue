<script lang="ts" setup>
const { document } = defineProps<{ document: Document }>();
// const document = {
// 	title: "Fimzo",
// 	tags: ["chicken", "jockey"],
// 	summary:
// 		"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed vehicula, neque suscipit cursus facilisis, ligula ipsum laoreet nulla, id bibendum ligula nunc et turpis. Integer eleifend accumsan cursus. Pellentesque a efficitur tortor. Phasellus fermentum dui non sapien fermentum ultricies. Fusce scelerisque orci ut turpis sodales commodo. In ultricies neque in volutpat ultrices. Nunc ornare, dolor nec pharetra accumsan, diam felis fringilla quam, et maximus dui neque sed turpis. Integer dignissim mauris nunc, ac bibendum nunc mollis nec. Fusce sagittis velit vitae ante auctor faucibus. Phasellus pharetra elit in nisi pharetra, nec sagittis nisl pellentesque. Nullam dignissim ligula vel suscipit tristique. Phasellus mattis, est in pharetra mattis, metus odio vehicula tortor, non consequat eros enim eu justo. Sed accumsan quam lorem, id sollicitudin neque venenatis ac. Nulla ut consectetur diam. ",
// 	recommendation:
// 		"aldsk jflkdsaflkfdsalkfdsafdsadsalgsaljgsaljgdsahjgalaagdsfdsa;lkjafds ;lkjafds;lkjafds;lkjafds;lkjfdsa;ljfdsa;lkj",
// 	blocks: [
// 		{
// 			title: "Am",
// 			text: "lorem ipsum shit",
// 		},
// 		{
// 			title: "Nya",
// 			text: "m lorem ipsum shit",
// 		},
// 	],
// };
</script>
<template>
	<div class="flex flex-col gap-3">
		<div class="text-6xl">{{ document.title }}</div>
		<div v-if="document.theme">{{ document.theme }}</div>
		<DocumentTags v-if="document.tags" :tags="document.tags" />
		<Headered v-if="document.summary" header="Краткое содержание">
			{{ document.summary }}
		</Headered>
		<Headered
			v-if="document.recommendations"
			header="Рекомендации по улучшению"
		>
			{{ document.recommendations }}
		</Headered>
		<div class="text-2xl font-medium">Смысловые блоки</div>
		<Blocks v-if="document.blocks" :blocks="document.blocks" />
	</div>
</template>
