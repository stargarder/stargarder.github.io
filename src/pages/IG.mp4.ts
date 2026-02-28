import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';

export const GET: APIRoute = async () => {
  const filePath = path.join(process.cwd(), 'public', '/Stargarder.mp4');
  
  const file = fs.readFileSync(filePath);
  
  return new Response(file, {
    headers: {
      'Content-Type': 'video/mp4',
      'Content-Disposition': 'attachment; filename="IG.mp4"',
      'Content-Length': file.length.toString(),
    },
  });
};
