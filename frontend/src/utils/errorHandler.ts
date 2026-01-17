import { message, notification } from 'antd';
import type { AxiosError } from 'axios';

export interface ErrorResponse {
  error_code: string;
  message: string;
  details?: Record<string, any>;
  path?: string;
}

/**
 * Handle API errors and display appropriate messages
 */
export function handleApiError(error: unknown): void {
  if (!error) {
    message.error('发生未知错误');
    return;
  }

  const axiosError = error as AxiosError<ErrorResponse>;

  // Network error
  if (!axiosError.response) {
    notification.error({
      message: '网络错误',
      description: '无法连接到服务器，请检查网络连接',
      duration: 5,
    });
    return;
  }

  const { status, data } = axiosError.response;
  const errorCode = data?.error_code || `HTTP_${status}`;
  const errorMessage = data?.message || '请求失败';
  const details = data?.details;

  // Handle specific error codes
  switch (errorCode) {
    case 'SESSION_EXPIRED':
      notification.warning({
        message: '会话已过期',
        description: '您的会话已过期，请重新开始',
        duration: 5,
      });
      break;

    case 'LLM_API_ERROR':
      notification.error({
        message: 'AI服务错误',
        description: errorMessage || 'AI服务暂时不可用，请稍后重试',
        duration: 8,
      });
      break;

    case 'DOCUMENT_PARSE_ERROR':
      notification.error({
        message: '文档解析失败',
        description: errorMessage || '文档格式不支持或文件已损坏',
        duration: 5,
      });
      break;

    case 'SCRIPT_EXECUTION_ERROR':
      notification.error({
        message: '脚本执行失败',
        description: errorMessage,
        duration: 5,
      });
      break;

    case 'KB_SEARCH_ERROR':
      notification.warning({
        message: '知识库检索失败',
        description: '知识库检索出错，将继续生成但不使用知识库',
        duration: 5,
      });
      break;

    case 'VALIDATION_ERROR':
      notification.error({
        message: '验证错误',
        description: errorMessage,
        duration: 5,
      });
      if (details?.errors && Array.isArray(details.errors)) {
        console.error('Validation errors:', details.errors);
      }
      break;

    case 'RESOURCE_NOT_FOUND':
      notification.error({
        message: '资源不存在',
        description: errorMessage,
        duration: 5,
      });
      break;

    case 'TIMEOUT_ERROR':
      notification.error({
        message: '请求超时',
        description: errorMessage || '操作超时，请重试',
        duration: 5,
      });
      break;

    case 'FILE_SIZE_EXCEEDED':
      notification.error({
        message: '文件过大',
        description: errorMessage || '文件大小超过10MB限制',
        duration: 5,
      });
      break;

    case 'UNSUPPORTED_FILE_TYPE':
      notification.error({
        message: '文件类型不支持',
        description: errorMessage,
        duration: 5,
      });
      break;

    default:
      // Generic error handling based on status code
      if (status >= 500) {
        notification.error({
          message: '服务器错误',
          description: errorMessage || '服务器遇到错误，请稍后重试',
          duration: 5,
        });
      } else if (status >= 400) {
        notification.error({
          message: '请求错误',
          description: errorMessage,
          duration: 5,
        });
      } else {
        message.error(errorMessage);
      }
  }

  // Log error details in development
  if (import.meta.env.DEV) {
    console.error('API Error:', {
      status,
      errorCode,
      message: errorMessage,
      details,
      path: data?.path,
    });
  }
}

/**
 * Show success message
 */
export function showSuccess(msg: string): void {
  message.success(msg);
}

/**
 * Show warning message
 */
export function showWarning(msg: string): void {
  message.warning(msg);
}

/**
 * Show info message
 */
export function showInfo(msg: string): void {
  message.info(msg);
}

/**
 * Show error message
 */
export function showError(msg: string): void {
  message.error(msg);
}
