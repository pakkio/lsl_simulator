"""
LSL Expression Node Pool - Object Pool Pattern for Memory Optimization
Addresses memory allocation concerns for complex LSL scripts with many AST nodes.
"""

from typing import Dict, List, Type, Any
from threading import Lock
import weakref
from lsl_expression_evaluator import (
    ExpressionNode, LiteralNode, VariableNode, ComponentAccessNode,
    UnaryOperatorNode, BinaryOperatorNode, FunctionCallNode, 
    TypeCastNode, ListLiteralNode
)


class NodePool:
    """Object pool for reusing ExpressionNode instances to reduce memory allocation."""
    
    def __init__(self, max_pool_size: int = 1000):
        self.max_pool_size = max_pool_size
        self._pools: Dict[Type, List[ExpressionNode]] = {}
        self._lock = Lock()
        self._stats = {
            'created': 0,
            'reused': 0,
            'returned': 0,
            'max_pool_sizes': {}
        }
        
        # Initialize pools for common node types
        self._pools[LiteralNode] = []
        self._pools[VariableNode] = []
        self._pools[BinaryOperatorNode] = []
        self._pools[FunctionCallNode] = []
        self._pools[ComponentAccessNode] = []
        self._pools[UnaryOperatorNode] = []
        self._pools[TypeCastNode] = []
        self._pools[ListLiteralNode] = []
    
    def get_node(self, node_type: Type, *args, **kwargs) -> ExpressionNode:
        """Get a node from the pool or create a new one."""
        with self._lock:
            pool = self._pools.get(node_type, [])
            
            if pool:
                # Reuse existing node
                node = pool.pop()
                self._reset_node(node, *args, **kwargs)
                self._stats['reused'] += 1
                return node
            else:
                # Create new node
                node = node_type(*args, **kwargs)
                self._stats['created'] += 1
                return node
    
    def return_node(self, node: ExpressionNode) -> None:
        """Return a node to the pool for reuse."""
        if node is None:
            return
            
        node_type = type(node)
        with self._lock:
            pool = self._pools.get(node_type, [])
            
            if len(pool) < self.max_pool_size:
                self._clear_node(node)
                pool.append(node)
                self._stats['returned'] += 1
                self._stats['max_pool_sizes'][node_type.__name__] = max(
                    self._stats['max_pool_sizes'].get(node_type.__name__, 0),
                    len(pool)
                )
    
    def _reset_node(self, node: ExpressionNode, *args, **kwargs) -> None:
        """Reset a pooled node with new values."""
        if isinstance(node, LiteralNode):
            node.value = args[0] if args else kwargs.get('value')
        elif isinstance(node, VariableNode):
            node.name = args[0] if args else kwargs.get('name')
        elif isinstance(node, ComponentAccessNode):
            node.variable = args[0] if args else kwargs.get('variable')
            node.component = args[1] if len(args) > 1 else kwargs.get('component')
        elif isinstance(node, UnaryOperatorNode):
            node.operator = args[0] if args else kwargs.get('operator')
            node.operand = args[1] if len(args) > 1 else kwargs.get('operand')
        elif isinstance(node, BinaryOperatorNode):
            node.left = args[0] if args else kwargs.get('left')
            node.operator = args[1] if len(args) > 1 else kwargs.get('operator')
            node.right = args[2] if len(args) > 2 else kwargs.get('right')
        elif isinstance(node, FunctionCallNode):
            node.name = args[0] if args else kwargs.get('name')
            node.args = args[1] if len(args) > 1 else kwargs.get('args', [])
        elif isinstance(node, TypeCastNode):
            node.target_type = args[0] if args else kwargs.get('target_type')
            node.expression = args[1] if len(args) > 1 else kwargs.get('expression')
        elif isinstance(node, ListLiteralNode):
            node.elements = args[0] if args else kwargs.get('elements', [])
    
    def _clear_node(self, node: ExpressionNode) -> None:
        """Clear a node's references to prevent memory leaks."""
        if isinstance(node, (UnaryOperatorNode, TypeCastNode)):
            node.operand = None
            node.expression = None
        elif isinstance(node, BinaryOperatorNode):
            node.left = None
            node.right = None
        elif isinstance(node, FunctionCallNode):
            node.args = []
        elif isinstance(node, ListLiteralNode):
            node.elements = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics for monitoring."""
        with self._lock:
            current_sizes = {
                node_type.__name__: len(pool) 
                for node_type, pool in self._pools.items()
            }
            
            return {
                'created': self._stats['created'],
                'reused': self._stats['reused'],
                'returned': self._stats['returned'],
                'reuse_rate': self._stats['reused'] / max(1, self._stats['created'] + self._stats['reused']),
                'current_pool_sizes': current_sizes,
                'max_pool_sizes': self._stats['max_pool_sizes'].copy()
            }
    
    def clear_pools(self) -> None:
        """Clear all pools (useful for testing or memory pressure)."""
        with self._lock:
            for pool in self._pools.values():
                pool.clear()


class PooledTreeToNodeConverter:
    """Enhanced TreeToNodeConverter that uses object pooling."""
    
    def __init__(self, simulator, node_pool: NodePool):
        self.simulator = simulator
        self.node_pool = node_pool
        self._active_nodes: List[ExpressionNode] = []
    
    def convert(self, parsed_tree) -> ExpressionNode:
        """Convert a pyparsing tree to a pooled ExpressionNode."""
        self._active_nodes.clear()
        result = self._convert_tree(parsed_tree)
        return result
    
    def _convert_tree(self, tree) -> ExpressionNode:
        """Internal conversion method using pooled nodes."""
        # Handle simple values
        if not isinstance(tree, list) and not hasattr(tree, 'asList'):
            if isinstance(tree, str):
                # Check if it's a component access
                if '.' in tree and not self._is_url_or_ip(tree):
                    var_name, component = tree.split('.', 1)
                    # Only treat as component access if variable exists
                    if self.simulator.call_stack.find_variable(var_name) is not None:
                        node = self.node_pool.get_node(ComponentAccessNode, var_name, component)
                        self._active_nodes.append(node)
                        return node
                # Return as variable reference
                node = self.node_pool.get_node(VariableNode, tree)
                self._active_nodes.append(node)
                return node
            else:
                # Literal value
                node = self.node_pool.get_node(LiteralNode, tree)
                self._active_nodes.append(node)
                return node
        
        # Convert to list format
        if hasattr(tree, 'asList'):
            items = tree.asList()
        else:
            items = tree
        
        # Handle nested structures
        if isinstance(items, list) and len(items) == 1 and isinstance(items[0], list):
            elements = [self._convert_tree(item) for item in items[0]]
            node = self.node_pool.get_node(ListLiteralNode, elements)
            self._active_nodes.append(node)
            return node
        
        # Handle vector/rotation literals
        if isinstance(items, list) and len(items) in [3, 4]:
            if all(isinstance(item, (int, float)) for item in items):
                elements = [self.node_pool.get_node(LiteralNode, item) for item in items]
                for elem in elements:
                    self._active_nodes.append(elem)
                node = self.node_pool.get_node(ListLiteralNode, elements)
                self._active_nodes.append(node)
                return node
        
        # Handle unary operators
        if len(items) == 2 and items[0] in ['!', '-', '+']:
            operand = self._convert_tree(items[1])
            node = self.node_pool.get_node(UnaryOperatorNode, items[0], operand)
            self._active_nodes.append(node)
            return node
        
        # Handle type casting
        if len(items) == 2 and items[0] in ["integer", "string", "float", "key"]:
            expression = self._convert_tree(items[1])
            node = self.node_pool.get_node(TypeCastNode, items[0], expression)
            self._active_nodes.append(node)
            return node
        
        # Handle function calls
        if isinstance(items, list) and len(items) >= 1 and isinstance(items[0], str):
            func_name = items[0]
            if (func_name.startswith('ll') or func_name.startswith('os') or 
                func_name in self.simulator.user_functions):
                args = [self._convert_tree(arg) for arg in items[1:]]
                node = self.node_pool.get_node(FunctionCallNode, func_name, args)
                self._active_nodes.append(node)
                return node
        
        # Handle binary operators
        if len(items) >= 3 and len(items) % 2 == 1:
            if self._is_binary_expression(items):
                result = self._build_binary_expression(items)
                return result
        
        # Default: treat as list literal
        elements = [self._convert_tree(item) for item in items]
        node = self.node_pool.get_node(ListLiteralNode, elements)
        self._active_nodes.append(node)
        return node
    
    def _is_url_or_ip(self, text: str) -> bool:
        """Check if text is a URL or IP address."""
        return ('://' in text or text.startswith('http') or 
                text.replace('.', '').replace(':', '').isdigit())
    
    def _is_binary_expression(self, items: List) -> bool:
        """Check if items represent a binary expression."""
        operators = ['+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '&', '|', '^', '<<', '>>']
        for i in range(1, len(items), 2):
            if i >= len(items) or not isinstance(items[i], str) or items[i] not in operators:
                return False
        return True
    
    def _build_binary_expression(self, items: List) -> ExpressionNode:
        """Build a binary expression tree from items using pooled nodes."""
        left = self._convert_tree(items[0])
        
        for i in range(1, len(items), 2):
            if i + 1 >= len(items):
                break
            operator = items[i]
            right = self._convert_tree(items[i + 1])
            node = self.node_pool.get_node(BinaryOperatorNode, left, operator, right)
            self._active_nodes.append(node)
            left = node
        
        return left
    
    def cleanup(self) -> None:
        """Return all active nodes to the pool."""
        for node in self._active_nodes:
            self.node_pool.return_node(node)
        self._active_nodes.clear()


# Global node pool instance
_global_node_pool = NodePool()

def get_global_node_pool() -> NodePool:
    """Get the global node pool instance."""
    return _global_node_pool