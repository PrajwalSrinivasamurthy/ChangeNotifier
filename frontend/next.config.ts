import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  basePath: "/changenotifier",
  trailingSlash: true,
};

export default nextConfig;
