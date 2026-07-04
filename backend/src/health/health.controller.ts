import { Controller, Get } from '@nestjs/common';
import { HealthResponseDto } from './dto/health-response.dto';

@Controller('health')
export class HealthController {
  @Get()
  health(): HealthResponseDto {
    return { status: 'ok' };
  }
}
