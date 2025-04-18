<script setup>
    // import { toTypedSchema } from '@vee-validate/zod'
    // import { useForm } from 'vee-validate'
    // import * as z from 'zod'
    //
    // const formSchema = toTypedSchema(z.object({
    //   username: z.string().min(2).max(50),
    // }))
    // const form = useForm({
    //   validationSchema: formSchema,
    // })
    //
    // const onSubmit = form.handleSubmit((values) => {
    //   console.log('Form submitted!', values)
    // })
    //
    // const test = function () {
    //     console.log("test")
    //     alert("test")
    //
    // }

    const onSubmit = function(v) {
        alert(JSON.stringify(v))
    }
</script>

<template>
    <div class="flex flex-col items-center min-h-screen p-5">
        <Form @submit="onSubmit" class="flex flex-col items-center min-h-screen p-5">
            <!-- <FormField  v-slot="{ componentField }" name="tag"> -->
            <!-- <FormField> -->
            <!--     <FormItem> -->
            <!--         <div class="items-top flex gap-x-2"> -->
            <!--             <Checkbox id="terms1" /> -->
            <!--             <div class="grid gap-1.5 leading-none"> -->
            <!--                 <label -->
            <!--                   for="terms1" -->
            <!--                   class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" -->
            <!--                 > -->
            <!--                 Теги -->
            <!--                 </label> -->
            <!--                 <p class="text-sm text-muted-foreground"> -->
            <!--                 Oписание -->
            <!--                 </p> -->
            <!--             </div> -->
            <!--         </div> -->
            <!--     </FormItem> -->
            <!-- </FormField> -->
            <!---->
            <!-- <FormField> -->
            <!--     <FormItem> -->
            <!--         <div class="items-top flex gap-x-2"> -->
            <!--             <Checkbox id="terms1" /> -->
            <!--             <div class="grid gap-1.5 leading-none"> -->
            <!--                 <label -->
            <!--                   for="terms1" -->
            <!--                   class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" -->
            <!--                 > -->
            <!--                 Анализ изображения -->
            <!--                 </label> -->
            <!--                 <p class="text-sm text-muted-foreground"> -->
            <!--                 Oписание -->
            <!--                 </p> -->
            <!--             </div> -->
            <!--         </div> -->
            <!--     </FormItem> -->
            <!-- </FormField> -->
            <!---->
            <!-- <FormField> -->
            <!--     <FormItem> -->
            <!--         <div class="items-top flex gap-x-2"> -->
            <!--             <Checkbox id="terms1" /> -->
            <!--             <div class="grid gap-1.5 leading-none"> -->
            <!--                 <label -->
            <!--                   for="terms1" -->
            <!--                   class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" -->
            <!--                 > -->
            <!--                 Рекомендации -->
            <!--                 </label> -->
            <!--                 <p class="text-sm text-muted-foreground"> -->
            <!--                 Oписание -->
            <!--                 </p> -->
            <!--             </div> -->
            <!--         </div> -->
            <!--     </FormItem> -->
            <!-- </FormField> -->
            <!-- <br> -->

            <FormField name="username">
                <FormItem>
                    <FormLabel>Промпт</FormLabel>
                    <FormControl>
                        <Textarea class="w-full" placeholder="Type your message here."/>
                    </FormControl>
                </FormItem>
                <FormMessage />
            </FormField>
            <br>
            <!-- <FormField> -->
            <!--     <FormItem> -->
            <!--         <FileUploader class="w-full"/> -->
            <!--     </FormItem> -->
            <!-- </FormField> -->
            <!-- <div class="h-10"></div> -->
            <Button type="submit" class="mx-auto">Анализировать</Button>
        </Form>
    </div>
</template>
