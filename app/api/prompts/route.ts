import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import fs from 'fs/promises';
import path from 'path';

const PROMPTS_DIR = path.join(process.cwd(), 'data', 'prompts');

async function ensureDir() {
  try {
    await fs.mkdir(PROMPTS_DIR, { recursive: true });
  } catch {}
}

// GET: List all prompt templates
export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ success: false, error: '未登录' }, { status: 401 });
    }

    await ensureDir();
    const files = await fs.readdir(PROMPTS_DIR);
    const templates = await Promise.all(
      files
        .filter((f) => f.endsWith('.txt'))
        .map(async (f) => {
          const content = await fs.readFile(path.join(PROMPTS_DIR, f), 'utf-8');
          return {
            id: f.replace('.txt', ''),
            name: f.replace('.txt', ''),
            content: content.trim(),
          };
        })
    );

    return NextResponse.json({ success: true, data: templates });
  } catch (error) {
    console.error('List prompts error:', error);
    return NextResponse.json({ success: false, error: '获取模板失败' }, { status: 500 });
  }
}

// POST: Create or update a prompt template
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ success: false, error: '未登录' }, { status: 401 });
    }

    const { name, content } = await request.json();
    if (!name || typeof name !== 'string' || !content || typeof content !== 'string') {
      return NextResponse.json({ success: false, error: '参数错误' }, { status: 400 });
    }

    // Sanitize filename
    const safeName = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]/g, '_').slice(0, 50);
    if (!safeName) {
      return NextResponse.json({ success: false, error: '名称无效' }, { status: 400 });
    }

    await ensureDir();
    const filePath = path.join(PROMPTS_DIR, `${safeName}.txt`);
    await fs.writeFile(filePath, content.trim(), 'utf-8');

    return NextResponse.json({
      success: true,
      data: { id: safeName, name: safeName, content: content.trim() },
    });
  } catch (error) {
    console.error('Create prompt error:', error);
    return NextResponse.json({ success: false, error: '创建模板失败' }, { status: 500 });
  }
}

// DELETE: Delete a prompt template
export async function DELETE(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ success: false, error: '未登录' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const name = searchParams.get('name');
    if (!name) {
      return NextResponse.json({ success: false, error: '缺少名称' }, { status: 400 });
    }

    const safeName = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]/g, '_');
    const filePath = path.join(PROMPTS_DIR, `${safeName}.txt`);

    try {
      await fs.unlink(filePath);
    } catch {
      return NextResponse.json({ success: false, error: '模板不存在' }, { status: 404 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Delete prompt error:', error);
    return NextResponse.json({ success: false, error: '删除模板失败' }, { status: 500 });
  }
}
