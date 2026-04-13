# React 基础知识

## 什么是 React

React 是 Facebook 开发的 JavaScript UI 库，用于构建用户界面。它的核心思想是组件化——把页面拆成一个个独立的、可复用的组件。

## 核心概念

### JSX

JSX 是 JavaScript 的语法扩展，允许在 JS 中写 HTML 风格的代码。它不是模板语言，最终会被编译成 React.createElement() 调用。

```jsx
const element = <h1>Hello, {name}</h1>;
```

### 组件

React 组件有两种写法：函数组件和类组件。现在推荐使用函数组件 + Hooks。

```jsx
function Welcome({ name }) {
  return <h1>Hello, {name}</h1>;
}
```

### Props

Props 是组件的输入参数，从父组件传递给子组件，是只读的。

```jsx
<Welcome name="Alice" />
```

### State

State 是组件的内部状态，用 useState Hook 管理。State 改变会触发组件重新渲染。

```jsx
const [count, setCount] = useState(0);
```

### useEffect

useEffect 用于处理副作用，比如数据获取、订阅、手动修改 DOM。

```jsx
useEffect(() => {
  fetchData();
}, [dependency]);
```

## React 生命周期

函数组件用 Hooks 替代了类组件的生命周期方法：
- componentDidMount → useEffect(() => {}, [])
- componentDidUpdate → useEffect(() => {}, [dep])
- componentWillUnmount → useEffect(() => { return () => cleanup }, [])

## 常用 Hooks

| Hook | 用途 |
|------|------|
| useState | 管理组件状态 |
| useEffect | 处理副作用 |
| useContext | 跨组件共享数据 |
| useRef | 引用 DOM 元素或保存可变值 |
| useMemo | 缓存计算结果 |
| useCallback | 缓存函数引用 |

## 状态管理

小项目用 useState + useContext，大项目用 Redux 或 Zustand。选择原则：能用简单方案就不要上复杂框架。

## 性能优化

1. React.memo — 避免不必要的重渲染
2. useMemo / useCallback — 缓存值和函数
3. 虚拟列表 — 大数据量列表用 react-window
4. 代码分割 — React.lazy + Suspense 按需加载
5. 避免在渲染中创建新对象/数组
