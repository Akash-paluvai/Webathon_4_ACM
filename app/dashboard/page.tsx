import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { prisma } from "@/lib/db";
import { getKindeServerSession } from "@kinde-oss/kinde-auth-nextjs/server";
import { BlogPostCard } from "@/components/general/BlogPostCard";
import { redirect } from "next/navigation";

async function getData(userId: string) {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    const data = await prisma.blogPost.findMany({
        where: {
            authorId: userId
        },
        orderBy: {
            createdAt: "desc"
        },
    })
    return data;
}

export default async function DashbordRoute() {

    const { getUser } = getKindeServerSession()
    const user = await getUser()

    if (!user) {
        return redirect("/api/auth/register")
    }

    const data = await getData(user.id)

    return (
        <div>
            <div className="flex item-center justify-between mb-4">
                <h2 className="text-xl font-medium">Your Blog Articles</h2>
                <Link href="/dashboard/create" className={buttonVariants()}>Create Post</Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {
                    data?.map((item) => (
                        <BlogPostCard key={item.id} data={item} />
                    ))
                }
            </div>
        </div>
    )
}