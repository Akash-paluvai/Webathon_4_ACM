// file to store all server actions/functions
//if server action is created in ext file like this, we have to specify 'use server' at the top of the doc instead of putting it in the function
//if we use it in a inline way and write the function in the form file (create/page.tsx) then specify it inside the function
"use server"

import { getKindeServerSession } from "@kinde-oss/kinde-auth-nextjs/server";
import { prisma } from "../lib/db";
import { redirect } from "next/navigation";

export async function handleSubmission(formData: FormData) {

    const { getUser } = getKindeServerSession()
    const user = await getUser()

    if (!user) {
        return redirect("/api/auth/register")
    }

    const title_from_form = formData.get('title') as string
    const content_from_form = formData.get('content') as string
    const imageUrl_from_form = formData.get('imageurl') as string

    const data = await prisma.blogPost.create({
        data: {
            title: title_from_form,
            content: content_from_form,
            imageUrl: imageUrl_from_form,
            authorId: user?.id as string,
            authorName: user?.given_name as string,
            authorImage: user?.picture as string,
            createdAt: new Date(),
        }
    })

    return redirect("/dashboard")
}