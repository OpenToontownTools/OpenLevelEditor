// Hardware Skinning DNA ANIMPROP Fragment Shader
// Drewcification 122120

#version 430

uniform vec4 p3d_ColorScale;

in vec4 vColor;
in vec2 texcoord;

out vec4 color;

uniform sampler2D p3d_Texture0;

void main() {
	// Mix the Texture, ColorScale, and VertexColor to get the full color
	color = p3d_ColorScale * texture(p3d_Texture0, texcoord) * vColor;
}