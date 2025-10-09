// 导入 vue-router 的路由记录类型
import { RouteRecordRaw } from 'vue-router';

// 获取对象中所有 url 的工具函数
export function getAllUrls(obj: object) {
  // 存储所有找到的路由
  const routes: RouteRecordRaw[] = [];

  // 递归遍历对象的辅助函数
  function traverse(current: Record<string, any> | Array<any>) {
    // 如果当前值为空或不是对象类型，直接返回
    if (current == null || typeof current !== 'object') return;

    // 处理数组类型
    if (Array.isArray(current)) {
      // 遍历数组中的每个元素
      current.forEach(traverse);
      return;
    }

    // 处理普通对象
    for (const key in current) {
      // 如果找到 url 属性，将其添加到路由数组中
      if (key === 'url') {
        routes.push(current[key]);
      }
      // 递归处理对象的子属性
      traverse(current[key]);
    }
  }

  // 开始遍历对象
  traverse(obj);
  // 返回收集到的所有路由
  return routes;
}