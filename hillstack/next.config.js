/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const config = {
  output: 'standalone',
  async redirects() {
    return [
      {
        source: '/congress',
        destination: '/congress/bills',
        permanent: true,
      },
      {
        source: '/congress/bills/:slug',
        destination: '/congress/bills/:slug/overview',
        permanent: true,
      },
    ]
  },
};

export default config;
