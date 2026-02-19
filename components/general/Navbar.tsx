import Link from "next/link";
import { Button, buttonVariants } from "../ui/button";
import {RegisterLink, LoginLink, LogoutLink} from "@kinde-oss/kinde-auth-nextjs/components";
import { getKindeServerSession } from "@kinde-oss/kinde-auth-nextjs/server";

export async function Navbar() {

    const {getUser} = getKindeServerSession()
    const user = await getUser()

    return (
        <nav className="flex justify-between items-center py-5">
            <div className="flex items-center gap-6">
                <Link href="/">
                    <h1 className="font-semibold text-2xl">Blog<span className="text-blue-500">Charan</span></h1>
                </Link>
            </div>
            <div className="hidden sm:flex items-center gap-6">
                <Link className="text-sm font-medium hover:text-blue-500 transition-colors" href="/">Home</Link>
                <Link className="text-sm font-medium hover:text-blue-500 transition-colors" href="/dashboard">Dashboard</Link>
            </div>
            <div className="flex items-center gap-4">
                {user ? <div className="flex items-center gap-4">   
                    <p>{user.given_name}</p>  
                    <LogoutLink className={buttonVariants()}>Logout</LogoutLink>
                </div> : <div className="flex items-center gap-4">
                    <LoginLink className={buttonVariants()}>Login</LoginLink>
                    <RegisterLink className={buttonVariants({variant:"secondary"})}>Register</RegisterLink>
                </div>}
            </div>
        </nav>
    )
}