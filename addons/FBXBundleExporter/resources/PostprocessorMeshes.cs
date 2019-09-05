using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public class PostprocessorMeshes : AssetPostprocessor {

	protected ModelImporter ModelImporter {
		get {
			return (ModelImporter)assetImporter;
		}
	}


	private void OnPreprocessModel() {
		ModelImporter.importMaterials = false;//Don't generate Default Materials
		ModelImporter.useFileScale = false;
		ModelImporter.globalScale = 1.0f;
		ModelImporter.swapUVChannels = false;
	}


	private void OnPostprocessModel(GameObject gameObject) {
		MapMeshColliders(gameObject);
	}


	private void MapMeshColliders(GameObject gameObject) {
		//Find all renderers (MeshRender, SkinRender,...)
		Renderer[] renders = gameObject.GetComponentsInChildren<Renderer>();
		Dictionary<string, Renderer> nameRenders = new Dictionary<string, Renderer>();
		foreach (Renderer render in renders) {
			string name = render.name.Replace("_","").Replace(" ","");
			if (!nameRenders.ContainsKey(name)) {
				nameRenders.Add(name, render);
			}
		}
		List<GameObject> destroy = new List<GameObject>();

		//Find COLLIDER renders and map to target render
		foreach (Renderer render in renders) {
			if (render.name.Contains("COLLIDER")) {
				//Name to find
				string name = render.name.Replace("_","").Replace(" ","").Replace("COLLIDER","");
				if (nameRenders.ContainsKey(name)) {
					//Found a match, add MeshCollider to target render
					MeshCollider meshCollider = nameRenders[name].gameObject.AddComponent<MeshCollider>();
					if (render.GetComponent<MeshFilter>()) {
						meshCollider.sharedMesh = render.GetComponent<MeshFilter>().sharedMesh;
						destroy.Add(render.gameObject);
					}
				}
			}
		}
		//Destroy gameObjects with 'COLLIDER' renders as we don't want to display them
		for (int i = 0; i < destroy.Count; i++) {
			GameObject.DestroyImmediate(destroy[i]);
		}
	}


	public Material OnAssignMaterialModel(Material material, Renderer renderer) {
		string name = material.name;
		if (name.Length > 0 && name.Contains(".")) {
			name = name.Substring(0, name.IndexOf("."));
		}

		//Find all project materials, and match by name
		string[] materialIDs =  AssetDatabase.FindAssets("t:Material");

		foreach (string materialID in materialIDs) {
			string path = AssetDatabase.GUIDToAssetPath(materialID);
			string extension = Path.GetExtension(path);
			if (extension == ".mat") {
				string nameMaterial = Path.GetFileNameWithoutExtension(path);
				if (nameMaterial == name) {
					return AssetDatabase.LoadAssetAtPath<Material>(path);
				}
			}
		}

		//Crate Empty material?
		return null;
	}
}