// next.config.js
module.exports = {
  // Enable the user-selected environment only on the WIP branch deployment.
  // Vercel supplies this at build time; main keeps its existing default.
  env: {
    NEXT_PUBLIC_GULLYVERSE_WIP_DEFAULT: process.env.VERCEL_GIT_COMMIT_REF === 'work-in-progress-2027' ? '1' : '0',
  },
  serverExternalPackages: ['pdf-parse', '@napi-rs/canvas', 'tesseract.js', 'tesseract.js-core'],
  experimental: {
    serverActions: {
      bodySizeLimit: '5mb',
    },
  },
  webpack(config, { dev }) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    // Dev-only: webpack's on-disk cache repeatedly corrupts on Windows here
    // (PackFileCacheStrategy rename ENOENT → "Unexpected token" runtime
    // errors from mangled chunks). Memory cache trades warm-restart speed for
    // builds that can't rot mid-session. Production builds are unaffected.
    if (dev) {
      config.cache = { type: 'memory' };
    }

    return config;
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**.breezesnu.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'img.youtube.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
};
