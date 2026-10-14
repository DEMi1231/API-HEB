from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

app = FastAPI()

clientes =[]
ventas = []
Costo_televisor = 4500.00

class Cliente(BaseModel):
    id_cliente: int
    nombre_cliente: str
    direccion: str
    active: bool = True

class Venta(BaseModel):
    id_venta: int
    id_cliente:int
    cantidad: int = Field(gt=0)
    fecha_registro: datetime = Field(default_factory=datetime.now)

class Costo(BaseModel):
    nuevo_costo : float = Field(ge=0)

@app.get("/v1/api/clientes")
def obtener_clientes():
    total_clientes = len(clientes)

    return{
        "indicador": "Exito en la consulta",
        "Total_clientes": total_clientes,
        "Lista_clientes": clientes
    }

@app.post("/v1/api/clientes")
def agregar_cliente(nuevo_cliente: Cliente):

    for cliente_existente in clientes:
        if(cliente_existente.id_cliente == nuevo_cliente.id_cliente):
            raise HTTPException(status_code=400, detail="El ID del cliente ya existe")
        
    clientes.append(nuevo_cliente)

    return{
        "mensaje": "Cliente registrado",
        "cliente": nuevo_cliente
    }

@app.put("/v1/api/clientes/{id_cliente}")
def actualizar_cliente(id_cliente: int, cliente_actualizado: Cliente):
    for cliente_existente in clientes:
        if(cliente_existente.id_cliente == id_cliente):
            cliente_existente.nombre_cliente = cliente_actualizado.nombre_cliente
            cliente_existente.direccion = cliente_actualizado.direccion
            cliente_existente.active = cliente_actualizado.active
            return{
                "mensaje": "Datos actualizados correctamente",
                "Nuevo nombre cliente": cliente_actualizado.nombre_cliente,
                "Nueva direccion cliente": cliente_actualizado.direccion,
                "Nueva estado cliente": cliente_actualizado.active
            }
    raise HTTPException(status_code=404, detail="El ID del cliente no existe")

@app.delete("/v1/api/clientes/{id_cliente}")
def desactivar_cliente(id_cliente: int):
    for cliente_existente in clientes:
        if(cliente_existente.id_cliente == id_cliente):
            cliente_existente.active = False
            return{
                "mensaje": "Cliente desactivado con exito",
                "Estado": cliente_existente.active
            }
    raise HTTPException(status_code=404, detail="El ID del cliente no existe")

@app.put("/v1/api/costo")
def modificar_costo(datos_costo: Costo):
    global Costo_televisor 
    Costo_televisor = datos_costo.nuevo_costo

    return{
        "mensaje": "Nuevo costo agregado",
        "Nuevo Costo": Costo_televisor
    }

@app.post("/v1/api/ventas")
def registrar_venta(nueva_venta: Venta):
    cliente_encontrado = False
    for cliente in clientes:
        if(cliente.id_cliente == nueva_venta.id_cliente):
            if(cliente.active == False):
                raise HTTPException(status_code=400, detail="No se puede vender a un cliente inactivo")
            else:
                cliente_encontrado = True
                break
    if(cliente_encontrado == False):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    ventas.append(nueva_venta)

    return{
        "Mensaje": "Venta correcta",
        "id cliente": nueva_venta.id_cliente,
        "cantidad": nueva_venta.cantidad,
        "fecha de registro": nueva_venta.fecha_registro
    }

@app.get("/v1/api/ventas")
def consultar_ventas(fecha: Optional[date] = None):
    global Costo_televisor
    reporte = []

    for venta in ventas:
        for cliente in clientes:
            if(cliente.id_cliente == venta.id_cliente):
                if(cliente.active == False):
                    continue
                if(fecha is not None and venta.fecha_registro.date() != fecha):
                    continue
                total_venta = venta.cantidad * Costo_televisor
                diccionario = {
                    "Cantidad":venta.cantidad,
                    "Fecha registro": venta.fecha_registro, 
                    "Costo":Costo_televisor,
                    "total venta": total_venta,
                    "cliente":{
                        "id Cliente": cliente.id_cliente,
                        "Nombre Cliente": cliente.nombre_cliente,
                        "Direccion": cliente.direccion
                    }
                }
                reporte.append(diccionario)
    return{
        "lista": reporte
    }

@app.put("/v1/api/ventas/{id_venta}")
def actualizar_venta(id_venta: int, venta_actualizada: Venta):
    venta_encontrada = None

    for venta in ventas:
        if(venta.id_venta == id_venta):
            venta_encontrada = venta
            break
    if(venta_encontrada is None):
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    for cliente in clientes:
        if (cliente.id_cliente == venta_actualizada.id_cliente):
            if(cliente.active == False):
                raise HTTPException(status_code=400, detail="No puedes actualizar una venta de cliente inactivo")
    venta_encontrada.cantidad = venta_actualizada.cantidad
    venta_encontrada.fecha_registro = venta_actualizada.fecha_registro
    venta_encontrada.id_cliente = venta_actualizada.id_cliente
    return{
        "Mensaje": "Registro correcto",
        "Nueva cantidad": venta_encontrada.cantidad,
        "Fecha de registro": venta_encontrada.fecha_registro,
        "Id cliente": venta_encontrada.id_cliente
    }

