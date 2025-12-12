import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { generateImage } from '@/lib/sora-api';
import { saveGeneration, updateUserBalance, getUserById, updateGeneration, getSystemConfig } from '@/lib/db';

export const maxDuration = 120;
export const dynamic = 'force-dynamic';

interface SoraImageRequest {
  prompt: string;
  model?: string;
  size?: string;
  input_image?: string;
}

// 后台处理任务
async function processGenerationTask(
  generationId: string,
  userId: string,
  body: SoraImageRequest
): Promise<void> {
  try {
    console.log(`[Task ${generationId}] 开始处理 Sora 图像生成任务`);

    await updateGeneration(generationId, { status: 'processing' });

    // 调用非流式 API
    const result = await generateImage({
      prompt: body.prompt,
      model: body.model || 'sora-image',
      size: body.size,
      input_image: body.input_image,
      response_format: 'url',
    });

    if (!result.data || result.data.length === 0 || !result.data[0].url) {
      throw new Error('图片生成失败：未返回有效的图片 URL');
    }

    const config = await getSystemConfig();
    const cost = config.pricing.soraImage || 1;

    console.log(`[Task ${generationId}] 生成成功:`, result.data[0].url);

    await updateUserBalance(userId, -cost);

    await updateGeneration(generationId, {
      status: 'completed',
      resultUrl: result.data[0].url,
    });

    console.log(`[Task ${generationId}] 任务完成`);
  } catch (error) {
    console.error(`[Task ${generationId}] 任务失败:`, error);

    await updateGeneration(generationId, {
      status: 'failed',
      errorMessage: error instanceof Error ? error.message : '生成失败',
    });
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: '请先登录' }, { status: 401 });
    }

    const body: SoraImageRequest = await request.json();

    if (!body.prompt) {
      return NextResponse.json(
        { error: '请输入提示词' },
        { status: 400 }
      );
    }

    const user = await getUserById(session.user.id);
    if (!user) {
      return NextResponse.json({ error: '用户不存在' }, { status: 401 });
    }

    const config = await getSystemConfig();
    const estimatedCost = config.pricing.soraImage || 1;

    if (user.balance < estimatedCost) {
      return NextResponse.json(
        { error: `余额不足，需要至少 ${estimatedCost} 积分` },
        { status: 402 }
      );
    }

    const generation = await saveGeneration({
      userId: user.id,
      type: 'sora-image',
      prompt: body.prompt,
      params: {
        model: body.model,
        size: body.size,
      },
      resultUrl: '',
      cost: estimatedCost,
      status: 'pending',
    });

    processGenerationTask(generation.id, user.id, body).catch((err) => {
      console.error('[API] Sora Image 后台任务启动失败:', err);
    });

    return NextResponse.json({
      success: true,
      data: {
        id: generation.id,
        status: 'pending',
        message: '任务已创建，正在后台处理中',
      },
    });
  } catch (error) {
    console.error('[API] Sora Image generation error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '生成失败' },
      { status: 500 }
    );
  }
}
