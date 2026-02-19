import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images:{
    remotePatterns:[
      {
        protocol:"https",
        hostname:"www.chitkara.edu.in",
        port:"",
      },{
        protocol:"https",
        hostname:"lh3.googleusercontent.com",
        port:"",
      }
    ]
  }
};

export default nextConfig;
