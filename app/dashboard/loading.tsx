//there are 2 ways to add streaming (ui while content is loading)
//1. using <Suspense> (in page.tsx)  (we can add manual suspense boundaries)
//2. using loading.tsx (in dashboard folder) (automatic suspense boundary of entire page)

//this is using loading.tsx style of streaming where entire page content is replaced by skeleton(style from shadcn)
import { Skeleton } from "@/components/ui/skeleton";


export default function LoadingDashboard(){
    return(
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Skeleton className="w-full h-[400px]"/>
            <Skeleton className="w-full h-[400px]"/>
            <Skeleton className="w-full h-[400px]"/>
        </div>
    )
}