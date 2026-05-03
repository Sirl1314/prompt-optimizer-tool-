import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  ThunderboltOutlined, HistoryOutlined, SwapOutlined,
  SettingOutlined, ApiOutlined,
} from '@ant-design/icons';

const { Sider, Content, Header } = Layout;

const menuItems = [
  { key: '/workbench', icon: <ThunderboltOutlined />, label: '工作台' },
  { key: '/history', icon: <HistoryOutlined />, label: '历史记录' },
  { key: '/compare', icon: <SwapOutlined />, label: '对比' },
  { key: '/domains', icon: <SettingOutlined />, label: '领域配置' },
  { key: '/models', icon: <ApiOutlined />, label: '模型管理' },
];

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ height: 48, margin: 16, color: '#fff', textAlign: 'center', fontWeight: 700, fontSize: collapsed ? 14 : 16 }}>
          {collapsed ? 'PO' : 'Prompt 优化工具'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', paddingLeft: 24, fontSize: 18, fontWeight: 600, borderBottom: '1px solid #f0f0f0' }}>
          Prompt 智能优化评测工具
        </Header>
        <Content style={{ margin: 16, padding: 24, background: '#fff', borderRadius: 8, minHeight: 360 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
