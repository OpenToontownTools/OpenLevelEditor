// Hardware Skinning DNA ANIMPROP Vertex Shader
// Drewcification 122120

#version 430
in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 transform_weight;
in uvec4 transform_index;

uniform mat4 p3d_ModelViewProjectionMatrix;

uniform mat4 p3d_TransformTable[100];

out vec4 vColor;
out vec2 texcoord;

void main() {
	// calculates the positions of the vertices for the animation

	mat4 animMatrix = p3d_TransformTable[transform_index.x] * transform_weight.x
				+ p3d_TransformTable[transform_index.y] * transform_weight.y
				+ p3d_TransformTable[transform_index.z] * transform_weight.z
				+ p3d_TransformTable[transform_index.w] * transform_weight.w;

	gl_Position = p3d_ModelViewProjectionMatrix * animMatrix * p3d_Vertex;

	vColor = p3d_Color;
	texcoord = p3d_MultiTexCoord0;
}