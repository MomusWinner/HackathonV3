<script setup lang="ts">
import {
	FormControl,
	FormDescription,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";

import { marked } from 'marked';
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { useUserStore } from "@/stores/user";
import { useDocumentStore } from "@/stores/documents";
import { Loader2 } from 'lucide-vue-next'
import { h } from "vue";
import * as z from "zod";

const loading = ref(false)

const userStore = useUserStore();
const documentStore = useDocumentStore();

const formSchema = toTypedSchema(
	z.object({
		prompt: z.string().max(100).default(""),
		show_tags: z.boolean().default(false),
		show_recommendations: z.boolean().default(false),
		analyze_images: z.boolean().default(false),
		show_topics: z.boolean().default(false),
		file: z.instanceof(File).refine((file) => file.size < 7000000, {
			message: "Your resume must be less than 7MB.",
		}),
	}),
);

const { isFieldDirty, handleSubmit } = useForm({
	validationSchema: formSchema,
	initialValues: {
		show_tags: true,
		show_recommendations: true,
		analyze_images: true,
		show_topics: true,
	},
});

const onSubmit = handleSubmit(async (values) => {
	const formData = new FormData();
	// Append all form values to FormData
	formData.append("user_id", userStore.getUser());
	Object.entries(values).forEach(([key, value]) => {
		// Handle both single files and file lists
		if (
			value instanceof File ||
			(Array.isArray(value) && value.every((item) => item instanceof File))
		) {
			if (Array.isArray(value)) {
				value.forEach((file) => formData.append(key, file));
			} else {
				formData.append(key, value);
			}
		} else {
			formData.append(key, value);
		}
	});

    loading.value = true
	const response = await fetch("http://localhost:8000/api/v1/documents/", {
		origin: "*",
		body: formData,
		method: "post",
	});
	const contentType = response.headers.get("content-type");
	let data;
	if (contentType && contentType.includes("application/json")) {
		data = await response.json();
        loading.value = false
	}
	// documentStore.setupWebSocketListener(data.ws_url);
	navigateTo(`/document/${data.id}`);
});
</script>

<template>
	<form class="p-5 space-y-6" @submit="onSubmit">
		<FormField v-slot="{ value, handleChange }" name="show_tags">
			<FormItem>
				<FormControl>
					<div class="items-top flex gap-x-2">
						<Checkbox
							id="terms1"
							:model-value="value"
							@update:model-value="handleChange"
						/>
						<div class="grid gap-1.5 leading-none">
							<label
								for="terms1"
								class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
							>
								Теги
							</label>
						</div>
					</div>
				</FormControl>
			</FormItem>
		</FormField>

		<FormField v-slot="{ value, handleChange }" name="show_recommendations">
			<FormItem>
				<FormControl>
					<div class="items-top flex gap-x-2">
						<Checkbox
							id="terms1"
							:model-value="value"
							@update:model-value="handleChange"
						/>
						<div class="grid gap-1.5 leading-none">
							<label
								for="terms1"
								class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
							>
								Рекомендации
							</label>
						</div>
					</div>
				</FormControl>
			</FormItem>
		</FormField>

		<FormField v-slot="{ value, handleChange }" name="analyze_images">
			<FormItem>
				<FormControl>
					<div class="items-top flex gap-x-2">
						<Checkbox
							id="terms1"
							:model-value="value"
							@update:model-value="handleChange"
						/>
						<div class="grid gap-1.5 leading-none">
							<label
								for="terms1"
								class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
							>
								Анализ изображений
							</label>
						</div>
					</div>
				</FormControl>
			</FormItem>
		</FormField>

		<FormField v-slot="{ value, handleChange }" name="show_topics">
			<FormItem>
				<FormControl>
					<div class="items-top flex gap-x-2">
						<Checkbox
							id="terms1"
							:model-value="value"
							@update:model-value="handleChange"
						/>
						<div class="grid gap-1.5 leading-none">
							<label
								for="terms1"
								class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
							>
								Темы
							</label>
						</div>
					</div>
				</FormControl>
			</FormItem>
		</FormField>

		<FormField v-slot="{ componentField }" name="file">
			<FormItem>
				<FormLabel>Файл</FormLabel>
				<FileUploader :field="componentField" />
				<FormMessage />
			</FormItem>
		</FormField>

		<FormField
			v-slot="{ componentField }"
			name="prompt"
			:validate-on-blur="!isFieldDirty"
		>
			<FormItem>
				<FormLabel>Пожелания</FormLabel>
				<FormControl>
					<Textarea placeholder="Повеселее" v-bind="componentField" />
				</FormControl>
				<!-- <FormDescription> This is your public display name. </FormDescription> -->
				<FormMessage />
			</FormItem>
		</FormField>

        <Button type="submit" :disable="loading">
             <Loader2 v-if="loading" class="w-4 h-4 mr-2 animate-spin" />
                Анализировать 
        </Button>
	</form>

    <div class="markdown-content" v-html="marked('### 1\n**')"></div>
</template>
