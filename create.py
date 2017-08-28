from PIL import Image
import random
import os,sys,math,time

#Devuelvo la lista de colores (R,G,B) y nombres de fotos
def cargo_vec_desde_file(path):
	archivo = open(path, "r")
	lista = []
	for linea in archivo.readlines():
		linea.replace("\n","")
		vec = linea.split(",")
		x = ((int) (vec[0]))
		y = ((int) (vec[1]))
		z = ((int) (vec[2]))
		n = vec[3].replace("\n","")
		lista.append((x,y,z,n))
	
	return lista

#Leo las fotos y asigno a cada foto un nombre y el color promedio que tienen.
#Guardo todo en un archivo para levantarlo facil.	
def crea_vec_promedios(path,salto,nombre):
	#Abro o creo archivo.txt
	f = open(nombre,'w')
	#Recorro las fotos de mi set de datos.
	for file in os.listdir(path):
		if file.endswith(".jpg"):
			print(file)
			name = os.path.join(path, file)
			#Abro imagen
			im = Image.open(name)
			vec = tomar_promedio_rgb(im,salto)
			#Escribo en el archivo el R,G,B y el nombre de la foto en cada linea
			f.write(str(vec[0])+","+str(vec[1])+","+str(vec[2])+","+file+"\n")
	f.close()

#Devuelvo el promedio de la suma de los colores que se encuentran en
#cada interseccion de la grilla.
#La grilla se crea eligiendo los pixeles a distancia "salto".
def tomar_promedio_rgb(im,salto):
	#Traigo matriz de pixeles
	pix = im.load()
	x,y=im.size
	r,g,b = 0,0,0
	total = 0
	#Incremento cada color (Red,Green y Blue) con el color de la interseccion
	for i in range(0,x,salto):
		for j in range(0,y,salto):
			total+=1
			r,g,b = r+pix[i,j][0],g+pix[i,j][1],b+pix[i,j][2]
	#Devuelvo el promedio de cada color(Red,Green y Blue)
	return (r//total,g//total,b//total)	

#Distancia algebraica entre 2 vectores de 3 coordenadas.
def distancia_euclidiana(r1,g1,b1,r2,g2,b2):
	r = (r1-r2)
	g = (g1-g2)
	b = (b1-b2)
	res =  r*r+g*g+b*b
	return math.sqrt(res)

#Funcion para recorrer pixeles	
def funcion_principal(region,lista,foto_path):
	#Elijo de que ancho quiero la grilla para la foto principal (1 porque solo proceso 1 foto lo que lo hace rapido)
	ancho_de_grilla = 1
	#Calculo los colores (R,G,B) que tiene esta region
	rgb_region = tomar_promedio_rgb(region,ancho_de_grilla)
	
	#Asigno un valor de distancia muy alto para luego reemplazar en el calculo de minimos
	#La distancia maxima puede ser raiz de 3 multiplicado por 256; por lo tanto 999 es mayor
	minimo=999
	foto_mas_cerca = ""
	
	#Itero mi set de datos y calculo la distancia entre cada foto del set y mi region
	for elem in lista:
		calc = distancia_euclidiana(rgb_region[0],rgb_region[1],rgb_region[2],elem[0],elem[1],elem[2])
		if(calc<=minimo):
			minimo=calc
			foto_mas_cerca=elem[3]
				
	#Devuelvo el path de la foto a elegir
	return foto_path+"/"+foto_mas_cerca

	
	
def apply_to_image(file_name, step_size,file_promedios,foto_path,times):
	HS = step_size
	WS = step_size
	
	#Creo un diccionario para almacenar las fotos en caso de necesitar repetir 
	memo = {}
	
	#Abro la imagen
	im = Image.open(file_name)
	
	#Creo una imagen nueva con dimensiones "times" veces mas grandes grandes
	#para no perder tantos pixeles al reducir las fotos.
	#El producto final va a "times" al cuadrado veces mas grande
	new_im = Image.new('RGB', (times*im.width,times*im.height))
	
	#Leo mi set de datos
	lista = cargo_vec_desde_file(file_promedios)
	
	#Para imprimir por pantalla el porcentaje de trabajo realizado
	diez_porciento = im.height//10
	pcnt=0
	comp=0
	
	#Recorro la imagen principal y armo las regiones
	for h in range(0,im.height,HS):
		#Imprime cada vez que avanza un 10 %
		if(h>=comp):
			comp+=diez_porciento
			print("Voy "+str(pcnt)+"% Altura: "+str(h))
			pcnt+=10
			
		for w in range(0,im.width,WS):
		
			#Creo la caja a recortar
			box = (w,h,(w+WS),(h+HS))
			region = im.crop(box)
			
			#Pido el nombre de la foto que mas se parece a la region que recorte
			nombre = funcion_principal(region,lista,foto_path)
			#Si el nombre no esta en mi diccionario lo agrego
			if(not (nombre in memo)):
				tmp = Image.open(nombre)
				#Agrando la region "times" veces para que la foto final sea mas grande
				memo[nombre] = tmp.resize((times*WS,times*HS),Image.NEAREST)
				
			#Agrando la caja "times" veces para colocar la nueva imagen
			box = (times*w,times*h,times*(w+WS),times*(h+HS))
			#Pego la nueva foto donde corresponde
			new_im.paste(memo[nombre],box)
	#Guardo la foto como archivo "JPEG"
	new_im.save("imaginate_"+file_name, "JPEG", quality=80, optimize=True, progressive=True)

	
	return new_im

#Empiezo un contador de tiempo para ver cuanto tarda	
start = time.time()
print("Espere mientras produsco la imagen")		
###############
###Como usar###
###############

#Variables a completar o cambiar
#Carpeta donde estan las imagenes 
#En mi caso estaban en el mismo directorio que este archivo dentro de la carpeta "SuperSetDeDatos"
FOTO_PATH = "SuperSetDeDatos"	
#Nombre que utilizan para el ".txt" con los datos ya precalculados
FILE_PROMEDIOS = "promedios_super.txt"	
#Nombre de foto a recrear (debe estar en el mismo path que este archivo)
FOTO_ORIGINAL = ["261.jpg"]
#Distancia entre pixeles para recrear la grilla
TAMANIO_EN_PIXELES_SUB_IMAGENES = 10
#Cuantas veces al cuadrado mas grande queres que sea la foto final
#Con esto quiero decir que con "TIMES = 2", la foto es 4 veces mas grande (2 veces de alto y 2 de ancho)
TIMES= 2

#Recomiendo primero correr solo la funcion que analiza los datos "crea_vec_promedios"
#y luego dejarla comentada.
#La variable CALIDAD es la distancia entre puntos de la grilla que uno analiza
#En el set de datos
CALIDAD = 5
#crea_vec_promedios(FOTO_PATH+"/",CALIDAD,FILE_PROMEDIOS)

#Recordar que para recorrer la funcion principal debemos correr almenos una ves "crea_vec_promedios"
#Para tener el archivo ".txt" con los datos
#apply_to_image(FOTO_ORIGINAL,TAMANIO_EN_PIXELES_SUB_IMAGENES,FILE_PROMEDIOS,FOTO_PATH,TIMES).show()


#FOTO_ORIGINAL = ["bumeran.png", "konzerta.png", "laborum.png","logo_acaula.png","logo_navent_1.png" ,"logo_navent_2.png","logo_navent_3.png" ,"logo_navent_4.png", "logo_naventmedia.png", "Logo_naventVioleta.png","Logo_naventVioletaFdo.png","logo_zonajobs.png","logo_ubit.png" ,"logo_zonaprop.png","naventlogo2.jpg","multitrabajos.png"]
for ele in FOTO_ORIGINAL:
	apply_to_image(ele,TAMANIO_EN_PIXELES_SUB_IMAGENES,FILE_PROMEDIOS,FOTO_PATH,TIMES)
	print(ele)

#Finalizo e imprimo la duracion.
end = time.time()
print(end - start)


