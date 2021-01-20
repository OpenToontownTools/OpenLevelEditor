"""
    Shader Registry - drewcification 111420
    Static class to register and get shaders

    Shaders are registered at the games initialization
        from ott.ShaderRegistry import ShaderRegistry
        ShaderRegistry.register('render:black_and_white',
                                frag = 'phase_3/shaders/tt_sha_render_bandw.frag',
                                vert = 'phase_3/shaders/tt_sha_render_bandw.vert')

    They can be retrieved at any point during runtime
        from ott.ShaderRegistry import ShaderRegistry
        render.setShader(ShaderRegistry.get('render:black_and_white'))
"""

from panda3d.core import Shader


class ShaderRegistry:
    # Static shader dictionary
    shaders = {}

    @staticmethod
    def register(identifier: str, frag: str, vert: str):
        """
        Register shader

        All shaders must be in GLSL with separate .frag and .vert files!

        Shader identifiers should be formatted by where they are used

        e.g.:
            Full scene render effects are prefixed with 'render:'
            CheesyEffects are prefixed with  'ce:'
            Make-A-Toon shaders are prefixed with 'mat:'
            etc.

        :param identifier: Identifier string
        :param frag: Fragment shader file path
        :param vert: Vertex shader file path
        """
        shader = Shader.load(Shader.SL_GLSL, fragment = frag, vertex = vert)
        ShaderRegistry.shaders[identifier] = shader
        print(f'Registered shader {identifier}')

    @staticmethod
    def get(identifier: str) -> Shader:
        """
        Returns loaded shader

        :param identifier:
        :return: Shader
        """

        # Raise an exception if we load a shader we haven't registered yet
        if identifier not in ShaderRegistry.shaders:
            raise NotInRegistryError(identifier)

        return ShaderRegistry.shaders.get(identifier)


class NotInRegistryError(Exception):
    def __init__(self, identifier: str):
        self.identifier = identifier

    def __str__(self):
        return f'identifier {self.identifier} not in registry'
