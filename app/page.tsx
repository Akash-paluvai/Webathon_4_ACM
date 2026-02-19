import { prisma } from "@/lib/db"
import { BlogPostCard } from "@/components/general/BlogPostCard";
import { Suspense } from "react";

async function getData() {
  await new Promise((resolve) => setTimeout(resolve, 1000))
  const data = await prisma.blogPost.findMany({
    select: {
      title: true,
      content: true,
      imageUrl: true,
      authorName: true,
      authorImage: true,
      createdAt: true,
      id: true,
      authorId: true,
      updatedAt: true,
    }
  })
  return data;
}

export default function Home() {
  return (
    <div className="py-6">
      <h1 className="text-3xl font-bold tracking-right mb-8">Latest posts</h1>
      <Suspense fallback={<p>Loading...</p>}>
        <BlogPostss />
      </Suspense>
    </div>
  );
}

async function BlogPostss() {
  const data = await getData()
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.map((item) => (
        <BlogPostCard key={item.id} data={item} />
      ))}
    </div>
  )
}
