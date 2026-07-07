import { type NextRequest, NextResponse } from 'next/server'
import { updateSession } from '@/utils/supabase/middleware'

export async function middleware(request: NextRequest) {
  // Block access to sponsors and team pages
  const blockedPaths = ['/sponsors']
  if (blockedPaths.some(path => request.nextUrl.pathname.startsWith(path))) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return await updateSession(request)
}

export const config = {
  matcher: [
    '/admin/:path*',
    '/api/breeze-admin/:path*',
    '/sponsors/:path*',
  ],
}