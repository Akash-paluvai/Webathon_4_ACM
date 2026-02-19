import { prisma } from "@/lib/db"
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { notFound } from "next/navigation"

async function getData(id: string) {
    const data = await prisma.blogPost.findUnique({
        where: {
            id: id
        },
    });

    if (!data) {
        return notFound()
    }

    return data;
}

type PageProps = {
    params: Promise<{
        id: string;
    }>;
};


export default async function IDPage({ params }: PageProps) {
    const { id } = await params;
    const data = await getData(id);
    return (
        <div className="max-w-3xl mx-auto py-8 px-4">
            <Link className={buttonVariants({variant: "secondary"})} href="/dashboard">Back to posts</Link>
            <h1 className="text-3xl mb-4 font-bold tracking-tight">{data?.title}</h1>
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                    <div>
                        
                    </div>
                </div>
            </div>
        </div>
    )
}