import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import './App.css'

const { Header, Content } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center',
        background: '#001529',
        color: '#fff',
        fontSize: '20px',
        fontWeight: 'bold'
      }}>
        AI测试用例生成系统
      </Header>
      <Content style={{ padding: '24px' }}>
        <Routes>
          <Route path="/" element={
            <div style={{ 
              textAlign: 'center', 
              padding: '50px',
              background: '#fff',
              borderRadius: '8px'
            }}>
              <h1>欢迎使用AI测试用例生成系统</h1>
              <p style={{ fontSize: '16px', color: '#666', marginTop: '20px' }}>
                系统正在开发中...
              </p>
            </div>
          } />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App
