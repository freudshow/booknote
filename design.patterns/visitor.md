# 访问者模式（Visitor Pattern）


## 定义与核心思想  
访问者模式是一种**行为型设计模式**，其核心思想是**将数据结构与数据操作分离**。当需要为一组不同类型的对象添加新操作时，无需修改对象本身，只需新增一个“访问者”类来封装该操作，从而遵循“开闭原则”（对扩展开放、对修改关闭）。


## 核心角色  
1. **抽象元素（Element）**：声明接受访问者的方法（`Accept`），该方法将访问者作为参数。  
2. **具体元素（ConcreteElement）**：实现抽象元素的`Accept`方法，通常在方法中调用访问者的对应访问方法（传入自身）。  
3. **抽象访问者（Visitor）**：声明对每个具体元素的访问方法（`Visit`），方法参数为具体元素类型。  
4. **具体访问者（ConcreteVisitor）**：实现抽象访问者的`Visit`方法，定义对具体元素的实际操作。  
5. **对象结构（ObjectStructure）**：持有元素集合，提供遍历元素的方法，让访问者可以访问所有元素。  


## 一、C# 实现访问者模式  
C# 是面向对象语言，天然支持接口和类，实现访问者模式较为直观。以下以“几何图形（圆、矩形）的面积/周长计算”为例实现。


### 代码实现  
```csharp
using System;
using System.Collections.Generic;

// ------------------------------
// 1. 抽象元素（Element）：声明接受访问者的方法
// ------------------------------
public interface IElement
{
    // 接受访问者的方法，参数为抽象访问者
    void Accept(IVisitor visitor);
}

// ------------------------------
// 2. 具体元素（ConcreteElement）：实现接受方法
// ------------------------------
// 具体元素1：圆
public class Circle : IElement
{
    public int Radius { get; } // 半径

    public Circle(int radius)
    {
        Radius = radius;
    }

    // 接受访问者：调用访问者针对“圆”的访问方法
    public void Accept(IVisitor visitor)
    {
        visitor.Visit(this); // 将自身作为参数传入
    }
}

// 具体元素2：矩形
public class Rectangle : IElement
{
    public int Width { get; }  // 宽
    public int Height { get; } // 高

    public Rectangle(int width, int height)
    {
        Width = width;
        Height = height;
    }

    // 接受访问者：调用访问者针对“矩形”的访问方法
    public void Accept(IVisitor visitor)
    {
        visitor.Visit(this); // 将自身作为参数传入
    }
}

// ------------------------------
// 3. 抽象访问者（Visitor）：声明对所有具体元素的访问方法
// ------------------------------
public interface IVisitor
{
    // 访问“圆”的方法
    void Visit(Circle circle);
    // 访问“矩形”的方法
    void Visit(Rectangle rectangle);
}

// ------------------------------
// 4. 具体访问者（ConcreteVisitor）：实现具体操作
// ------------------------------
// 具体访问者1：计算面积
public class AreaVisitor : IVisitor
{
    // 计算圆的面积：π * r²
    public void Visit(Circle circle)
    {
        double area = Math.PI * circle.Radius * circle.Radius;
        Console.WriteLine($"圆的面积：{area:F2}");
    }

    // 计算矩形的面积：宽 * 高
    public void Visit(Rectangle rectangle)
    {
        int area = rectangle.Width * rectangle.Height;
        Console.WriteLine($"矩形的面积：{area}");
    }
}

// 具体访问者2：计算周长
public class PerimeterVisitor : IVisitor
{
    // 计算圆的周长：2 * π * r
    public void Visit(Circle circle)
    {
        double perimeter = 2 * Math.PI * circle.Radius;
        Console.WriteLine($"圆的周长：{perimeter:F2}");
    }

    // 计算矩形的周长：2 * (宽 + 高)
    public void Visit(Rectangle rectangle)
    {
        int perimeter = 2 * (rectangle.Width + rectangle.Height);
        Console.WriteLine($"矩形的周长：{perimeter}");
    }
}

// ------------------------------
// 5. 对象结构（ObjectStructure）：管理元素集合，提供遍历接口
// ------------------------------
public class ObjectStructure
{
    private List<IElement> _elements = new List<IElement>();

    // 添加元素到集合
    public void AddElement(IElement element)
    {
        _elements.Add(element);
    }

    // 让所有元素接受访问者的访问
    public void Accept(IVisitor visitor)
    {
        foreach (var element in _elements)
        {
            element.Accept(visitor); // 每个元素调用自己的Accept方法
        }
    }
}

// ------------------------------
// 测试代码
// ------------------------------
class Program
{
    static void Main(string[] args)
    {
        // 创建对象结构并添加元素
        ObjectStructure structure = new ObjectStructure();
        structure.AddElement(new Circle(5));       // 半径为5的圆
        structure.AddElement(new Rectangle(4, 6)); // 4x6的矩形

        // 创建访问者并执行操作
        IVisitor areaVisitor = new AreaVisitor();
        Console.WriteLine("=== 计算面积 ===");
        structure.Accept(areaVisitor); // 所有元素接受面积访问者

        IVisitor perimeterVisitor = new PerimeterVisitor();
        Console.WriteLine("\n=== 计算周长 ===");
        structure.Accept(perimeterVisitor); // 所有元素接受周长访问者
    }
}
```


### 输出结果  
```
=== 计算面积 ===
圆的面积：78.54
矩形的面积：24

=== 计算周长 ===
圆的周长：31.42
矩形的周长：20
```


## 二、C 语言实现访问者模式  
C 语言没有类和接口，需通过**结构体模拟类**、**函数指针模拟方法**来实现。核心思路与 C# 一致，但需手动处理类型区分和函数调用。


### 代码实现  
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 前置声明（避免循环依赖）
typedef struct Visitor Visitor;
typedef struct Circle Circle;
typedef struct Rectangle Rectangle;
typedef struct Element Element;
typedef struct ObjectStructure ObjectStructure;

// ------------------------------
// 1. 抽象访问者（Visitor）：用结构体+函数指针模拟
//    声明对所有具体元素的访问方法
// ------------------------------
struct Visitor {
    // 访问“圆”的函数指针（参数：访问者自身、圆）
    void (*VisitCircle)(Visitor* self, Circle* circle);
    // 访问“矩形”的函数指针（参数：访问者自身、矩形）
    void (*VisitRectangle)(Visitor* self, Rectangle* rect);
};

// ------------------------------
// 2. 具体元素（ConcreteElement）：用结构体+函数指针模拟
// ------------------------------
// 具体元素1：圆
struct Circle {
    int radius; // 半径
    // 接受访问者的函数指针（参数：圆自身、访问者）
    void (*Accept)(Circle* self, Visitor* visitor);
};

// 圆的Accept实现：调用访问者的VisitCircle方法
static void Circle_Accept(Circle* self, Visitor* visitor) {
    if (visitor->VisitCircle) {
        visitor->VisitCircle(visitor, self); // 传入自身
    }
}

// 创建圆的构造函数
Circle* Circle_Create(int radius) {
    Circle* circle = (Circle*)malloc(sizeof(Circle));
    circle->radius = radius;
    circle->Accept = Circle_Accept; // 绑定Accept方法
    return circle;
}

// 具体元素2：矩形
struct Rectangle {
    int width;  // 宽
    int height; // 高
    // 接受访问者的函数指针（参数：矩形自身、访问者）
    void (*Accept)(Rectangle* self, Visitor* visitor);
};

// 矩形的Accept实现：调用访问者的VisitRectangle方法
static void Rectangle_Accept(Rectangle* self, Visitor* visitor) {
    if (visitor->VisitRectangle) {
        visitor->VisitRectangle(visitor, self); // 传入自身
    }
}

// 创建矩形的构造函数
Rectangle* Rectangle_Create(int width, int height) {
    Rectangle* rect = (Rectangle*)malloc(sizeof(Rectangle));
    rect->width = width;
    rect->height = height;
    rect->Accept = Rectangle_Accept; // 绑定Accept方法
    return rect;
}

// ------------------------------
// 3. 统一元素类型（Element）：用于对象结构管理（C无泛型，需手动区分类型）
// ------------------------------
typedef enum {
    ELEMENT_CIRCLE,
    ELEMENT_RECTANGLE
} ElementType;

struct Element {
    ElementType type; // 元素类型（用于区分圆和矩形）
    union {           // 存储具体元素的指针
        Circle* circle;
        Rectangle* rect;
    } data;
};

// 创建圆元素
Element* Element_CreateCircle(Circle* circle) {
    Element* elem = (Element*)malloc(sizeof(Element));
    elem->type = ELEMENT_CIRCLE;
    elem->data.circle = circle;
    return elem;
}

// 创建矩形元素
Element* Element_CreateRectangle(Rectangle* rect) {
    Element* elem = (Element*)malloc(sizeof(Element));
    elem->type = ELEMENT_RECTANGLE;
    elem->data.rect = rect;
    return elem;
}

// ------------------------------
// 4. 具体访问者（ConcreteVisitor）：实现具体操作
// ------------------------------
// 具体访问者1：计算面积
typedef struct {
    Visitor base; // 继承访问者（C通过包含实现“继承”）
} AreaVisitor;

// 面积访问者：访问圆（计算面积）
static void AreaVisitor_VisitCircle(Visitor* self, Circle* circle) {
    double area = M_PI * circle->radius * circle->radius;
    printf("圆的面积：%.2f\n", area);
}

// 面积访问者：访问矩形（计算面积）
static void AreaVisitor_VisitRectangle(Visitor* self, Rectangle* rect) {
    int area = rect->width * rect->height;
    printf("矩形的面积：%d\n", area);
}

// 面积访问者的构造函数
AreaVisitor* AreaVisitor_Create() {
    AreaVisitor* visitor = (AreaVisitor*)malloc(sizeof(AreaVisitor));
    // 绑定访问方法
    visitor->base.VisitCircle = AreaVisitor_VisitCircle;
    visitor->base.VisitRectangle = AreaVisitor_VisitRectangle;
    return visitor;
}

// 具体访问者2：计算周长
typedef struct {
    Visitor base; // 继承访问者
} PerimeterVisitor;

// 周长访问者：访问圆（计算周长）
static void PerimeterVisitor_VisitCircle(Visitor* self, Circle* circle) {
    double perimeter = 2 * M_PI * circle->radius;
    printf("圆的周长：%.2f\n", perimeter);
}

// 周长访问者：访问矩形（计算周长）
static void PerimeterVisitor_VisitRectangle(Visitor* self, Rectangle* rect) {
    int perimeter = 2 * (rect->width + rect->height);
    printf("矩形的周长：%d\n", perimeter);
}

// 周长访问者的构造函数
PerimeterVisitor* PerimeterVisitor_Create() {
    PerimeterVisitor* visitor = (PerimeterVisitor*)malloc(sizeof(PerimeterVisitor));
    // 绑定访问方法
    visitor->base.VisitCircle = PerimeterVisitor_VisitCircle;
    visitor->base.VisitRectangle = PerimeterVisitor_VisitRectangle;
    return visitor;
}

// ------------------------------
// 5. 对象结构（ObjectStructure）：管理元素集合
// ------------------------------
#define MAX_ELEMENTS 10 // 最大元素数量
struct ObjectStructure {
    Element* elements[MAX_ELEMENTS]; // 元素数组
    int count; // 当前元素数量
};

// 初始化对象结构
ObjectStructure* ObjectStructure_Create() {
    ObjectStructure* structure = (ObjectStructure*)malloc(sizeof(ObjectStructure));
    structure->count = 0;
    return structure;
}

// 添加元素到对象结构
void ObjectStructure_AddElement(ObjectStructure* structure, Element* elem) {
    if (structure->count < MAX_ELEMENTS) {
        structure->elements[structure->count++] = elem;
    }
}

// 让所有元素接受访问者访问
void ObjectStructure_Accept(ObjectStructure* structure, Visitor* visitor) {
    for (int i = 0; i < structure->count; i++) {
        Element* elem = structure->elements[i];
        // 根据元素类型调用对应的Accept方法
        switch (elem->type) {
            case ELEMENT_CIRCLE:
                elem->data.circle->Accept(elem->data.circle, visitor);
                break;
            case ELEMENT_RECTANGLE:
                elem->data.rect->Accept(elem->data.rect, visitor);
                break;
        }
    }
}

// ------------------------------
// 测试代码
// ------------------------------
int main() {
    // 1. 创建元素
    Circle* circle = Circle_Create(5);               // 半径5的圆
    Rectangle* rect = Rectangle_Create(4, 6);        // 4x6的矩形

    // 2. 包装为统一元素类型
    Element* circleElem = Element_CreateCircle(circle);
    Element* rectElem = Element_CreateRectangle(rect);

    // 3. 创建对象结构并添加元素
    ObjectStructure* structure = ObjectStructure_Create();
    ObjectStructure_AddElement(structure, circleElem);
    ObjectStructure_AddElement(structure, rectElem);

    // 4. 面积访问者操作
    AreaVisitor* areaVisitor = AreaVisitor_Create();
    printf("=== 计算面积 ===\n");
    ObjectStructure_Accept(structure, &areaVisitor->base); // 传入基类访问者

    // 5. 周长访问者操作
    PerimeterVisitor* perimeterVisitor = PerimeterVisitor_Create();
    printf("\n=== 计算周长 ===\n");
    ObjectStructure_Accept(structure, &perimeterVisitor->base);

    // 释放内存（简化示例，实际需完整释放）
    free(perimeterVisitor);
    free(areaVisitor);
    free(structure);
    free(rectElem);
    free(circleElem);
    free(rect);
    free(circle);

    return 0;
}
```


### 输出结果  
```
=== 计算面积 ===
圆的面积：78.54
矩形的面积：24

=== 计算周长 ===
圆的周长：31.42
矩形的周长：20
```


## 总结  
- **C# 实现**：利用接口和类的特性，自然映射访问者模式的角色，代码简洁且符合面向对象思想。  
- **C 实现**：通过结构体模拟类、函数指针模拟方法、类型标签区分元素，手动管理多态逻辑，虽繁琐但可行。  

访问者模式的核心价值在于**分离“数据”与“操作”**，适合需要频繁为一组固定类型对象添加新操作的场景（如编译器语法树分析、文档格式转换等）。