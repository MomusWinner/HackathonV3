<script setup lang="ts">
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'

import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { h } from 'vue'
import * as z from 'zod'

const formSchema = toTypedSchema(z.object({
    prompt: z.string().min(10).max(100),
    show_tags: z.boolean().default(false), 
    show_recommendations: z.boolean().default(false), 
    analyze_images: z.boolean().default(false), 
    show_topics: z.boolean().default(false), 
    file: z.instanceof(File).refine((file) => file.size < 7000000, {
        message: 'Your resume must be less than 7MB.',
    }),
}))

const { isFieldDirty, handleSubmit} = useForm({
    validationSchema: formSchema,
    initialValues: {
        show_tags: true,
        recommendation: true,
        analyze_images: true,
        topics: true,
    },
})

const onSubmit = handleSubmit(async (values) => {
    alert(JSON.stringify(values, null, 2))
    const formData = new FormData();
    // Append all form values to FormData
    Object.entries(values).forEach(([key, value]) => {
    // Handle both single files and file lists
    if (value instanceof File || (Array.isArray(value) && value.every(item => item instanceof File))) {
        if (Array.isArray(value)) {
            value.forEach(file => formData.append(key, file));
        } else {
            formData.append(key, value);
        }
    } else {
        formData.append(key, value);
    }
    });
    formData.append("user_id", "fcd9822a-4049-48ca-974d-3ea8b70a01e3")
    fetch('http://localhost:8000/api/v1/documents/', {
        origin: '*',
        body: formData,
        method: "post",
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        throw new TypeError("Oops, we haven't got JSON!");
    })
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
})

</script>

<template>
  <form class="w-2/3 space-y-6" @submit="onSubmit">
    <FormField v-slot="{ value, handleChange }" name="show_tags">
      <FormItem>
        <FormControl>
            <div class="items-top flex gap-x-2">
                <Checkbox id="terms1" :model-value="value" @update:model-value="handleChange"/>
                <div class="grid gap-1.5 leading-none">
                    <label
                      for="terms1"
                      class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                    Теги
                    </label>
                    <p class="text-sm text-muted-foreground">
                    Oписание
                    </p>
                </div>
            </div>
        </FormControl>
      </FormItem>
    </FormField>

    <FormField v-slot="{ value, handleChange }" name="show_recommendations">
      <FormItem>
        <FormControl>
            <div class="items-top flex gap-x-2">
                <Checkbox id="terms1" :model-value="value" @update:model-value="handleChange"/>
                <div class="grid gap-1.5 leading-none">
                    <label
                      for="terms1"
                      class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                    Рекомендации
                    </label>
                    <p class="text-sm text-muted-foreground">
                    Oписание
                    </p>
                </div>
            </div>
        </FormControl>
      </FormItem>
    </FormField>

    <FormField v-slot="{ value, handleChange }" name="analyze_images">
      <FormItem>
        <FormControl>
            <div class="items-top flex gap-x-2">
                <Checkbox id="terms1" :model-value="value" @update:model-value="handleChange"/>
                <div class="grid gap-1.5 leading-none">
                    <label
                      for="terms1"
                      class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                    Анализ изображений
                    </label>
                    <p class="text-sm text-muted-foreground">
                    Oписание
                    </p>
                </div>
            </div>
        </FormControl>
      </FormItem>
    </FormField>

    <FormField v-slot="{ value, handleChange }" name="show_topics">
      <FormItem>
        <FormControl>
            <div class="items-top flex gap-x-2">
                <Checkbox id="terms1" :model-value="value" @update:model-value="handleChange"/>
                <div class="grid gap-1.5 leading-none">
                    <label
                      for="terms1"
                      class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                    Темы
                    </label>
                    <p class="text-sm text-muted-foreground">
                    Oписание
                    </p>
                </div>
            </div>
        </FormControl>
      </FormItem>
    </FormField>


    <FormField v-slot="{ componentField }" name="file">
        <FormItem>
          <FormLabel>Файл</FormLabel>
            <FileUploader :field="componentField"  />
          <FormDescription>
            Upload your profile picture
          </FormDescription>
          <FormMessage />
        </FormItem>
    </FormField>

    <FormField v-slot="{ componentField }" name="prompt" :validate-on-blur="!isFieldDirty">
      <FormItem>
        <FormLabel>Промт</FormLabel>
        <FormControl>
          <Textarea placeholder="shadcn" v-bind="componentField" />
        </FormControl>
        <FormDescription>
          This is your public display name.
        </FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <Button type="submit">
    Анализировать
    </Button>
  </form>
</template>
