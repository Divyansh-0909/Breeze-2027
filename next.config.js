// next.config.js
module.exports = {
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
