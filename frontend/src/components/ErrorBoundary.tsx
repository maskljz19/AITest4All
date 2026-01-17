import { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <Result
            status="error"
            title="应用程序出错"
            subTitle="抱歉，应用程序遇到了一个错误。请尝试刷新页面或联系技术支持。"
            extra={[
              <Button type="primary" key="reload" onClick={this.handleReload}>
                刷新页面
              </Button>,
              <Button key="reset" onClick={this.handleReset}>
                返回
              </Button>,
            ]}
          >
            {import.meta.env.DEV && this.state.error && (
              <div style={{ textAlign: 'left', marginTop: 20 }}>
                <details style={{ whiteSpace: 'pre-wrap' }}>
                  <summary>错误详情 (仅开发环境显示)</summary>
                  <p style={{ color: 'red' }}>{this.state.error.toString()}</p>
                  {this.state.errorInfo && (
                    <p style={{ color: '#666' }}>
                      {this.state.errorInfo.componentStack}
                    </p>
                  )}
                </details>
              </div>
            )}
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
