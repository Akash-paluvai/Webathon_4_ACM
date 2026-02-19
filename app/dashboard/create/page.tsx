"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { SubmitButton } from "@/components/general/Submitbutton";
import { handleSubmission } from "@/app/actions";

export default function CreateBlogroute(){

    return(
        <div>
            <Card className="max-w-lg mx-auto mt-10">
                <CardHeader>
                    <CardTitle className="text-center">Create a new blog post</CardTitle>
                    <CardDescription className="text-center">Fill in the details below to create a new blog post</CardDescription>
                </CardHeader>
                <CardContent>
                    <form className="flex flex-col gap-4" action={handleSubmission}>
                    <   div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input name="title" required id="title" placeholder="Enter your blog post title" />
                        </div>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="content">Content</Label>
                            <Textarea name="content" required id="content" placeholder="Enter your blog post content" />
                        </div>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="imageurl">Image URL</Label>
                            <Input name="imageurl" required id="imageurl" placeholder="Image URL" />
                        </div>
                        <SubmitButton/>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}