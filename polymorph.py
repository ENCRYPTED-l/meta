class PolyDict(dict):
    """
    Словарь, который при сохранении одного и того же ключа
    оборачивает все его значения в один PolyMethod.
    """
    def __setitem__(self, key: str, func):
        if not key.startswith('_'):

            if key not in self:
                super().__setitem__(key, PolyMethod())
            self[key].add_implementation(func)
            return None

        return super().__setitem__(key, func)

class PolyMethod:
    """
    Обертка для полиморфного метода, которая хранит связь между типом аргумента
    и реализацией метода для данного типа. Для данного объекта мы реализуем
    протокол дескриптора, чтобы поддержать полиморфизм для всех типов методов:
    instance method, staticmethod, classmethod.
    """
    def __init__(self):
        self.implementations = {}
        self.instance = None
        self.cls = None

    def __get__(self, instance, cls):
        self.instance = instance
        self.cls = cls
        return self

    def _get_callable_func(self, impl):
        # "достаем" функцию classmethod/staticmethod
        return getattr(impl, '__func__', impl)

    def __call__(self, arg):
        impl = self.implementations[type(arg)]
        callable_func = self._get_callable_func(impl)

        if isinstance(impl, staticmethod):
            return callable_func(arg)
        elif self.cls and isinstance(impl, classmethod):
            return callable_func(self.cls, arg)
        else:
            return callable_func(self.instance, arg)

    def add_implementation(self, func):
        callable_func = self._get_callable_func(func)

        # расчитываем на то, что метод принимает только 1 параметр
        arg_name, arg_type = list(callable_func.__annotations__.items())[0]
        self.implementations[arg_type] = func

class PolyMeta(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        return PolyDict()

class Terminator(metaclass=PolyMeta):
    def terminate(self, x: int):
        print(f'Terminating INTEGER {x}')

    def terminate(self, x: str):
        print(f'Terminating STRING {x}')

    def terminate(self, x: dict):
        print(f'Terminating DICTIONARY {x}')

t1000 = Terminator()
t1000.terminate(10)
t1000.terminate('Hello, world!')
t1000.terminate({'hello': 'world'})

# Вывод
# Terminating
# INTEGER
# 10
# Terminating
# STRING
# Hello, world!
# Terminating
# DICTIONARY
# {'hello': 'world'}