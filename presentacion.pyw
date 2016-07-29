#Imports
from bs4 import BeautifulSoup
import urllib
import infoBolsa
import sys
import pymysql
from PyQt5.QtCore import QFile,QFileInfo,QPoint,QSettings,QSignalMapper,QSize,QTextStream,Qt,QCoreApplication
from PyQt5.QtGui import QIcon,QKeySequence,QTextDocument,QTextBlock,QStandardItemModel,QStandardItem,QBrush
from PyQt5.QtWidgets import QAction,QApplication,QFileDialog,QMainWindow,QMdiArea,QMessageBox, QTextEdit,QWidget, QMdiSubWindow,QTableWidgetItem
from PyQt5 import uic
import mdirc_

#Clase hija
class mdiChild(QMdiSubWindow):
  def __init__(self):
    super(mdiChild,self).__init__()

#Clase hija con diseño
class mdiChildUI(QMdiSubWindow):
  def __init__(self,archivoUI):
    super(mdiChildUI,self).__init__()
    uic.loadUi(archivoUI,self)

#Iniciar la base de datos en mysql
def iniciarBD(host,user,password,db):
  return pymysql.connect(host=host,user=user,password=password,db=db)


#Clase login. Sera una clase hija aparte de los mensionados por comodidad al usuario. 
class loginChild(QMdiSubWindow):
  def __init__(self):
    super(loginChild,self).__init__()
    uic.loadUi("login.ui",self)
    self.setWindowFlags(Qt.FramelessWindowHint)
    self.setAccessibleName("login")
    self.contrasenia.setEchoMode(2)

#Clase Bolsa de Valores formato richText
class iBolsaChild(QMdiSubWindow):
  def __init__(self):
    super(iBolsaChild,self).__init__()
    uic.loadUi("informacionBolsa.ui",self)
    listView=self.listView
    listView.setWindowTitle('Tweets relevantes')
    self.model = QStandardItemModel(listView)

#Clase ventana principal
class MainWindow(QMainWindow):
  administradorActive = 0
  def __init__(self):
    super(QMainWindow, self).__init__()
    uic.loadUi("mainwindow.ui",self)

    #Variables fijas
    self.conn=iniciarBD('localhost','BDERP','Bob1_esponj2','BDERP')
    self.cur=self.conn.cursor()
    self.mdiArea = QMdiArea()
    self.windowMapper = QSignalMapper(self)
    self.titlesProducto=["Id","Nombre","Precio","Cantidad"]
    self.titlesEmpleado=["ID","Nombre","Puesto"]
    self.iBolsa=infoBolsa.infBolsa()

    #Ventanas hijas
    self.login=loginChild()
    self.informacionBolsa = iBolsaChild()
    self.compras = mdiChildUI("compra.ui")
    self.ventas = mdiChildUI("venta.ui")
    self.RRHH = mdiChildUI("RRHH.ui")
    self.compraDetalle = mdiChildUI("compraDetalle.ui")
    self.ventaDetalle = mdiChildUI("ventaDetalle.ui")
    self.nuevoEmpleado = mdiChildUI("nuevoEmpleado.ui")
    self.nuevoCliente = mdiChildUI("nuevoCliente.ui")
    self.nuevoProveedor = mdiChildUI("agregarProveedor.ui")

    #Variables Auxiliares
    mdiArea=self.mdiArea
    login=self.login
    compras=self.compras
    compraDetalle=self.compraDetalle
    ventas=self.ventas
    ventaDetalle=self.ventaDetalle
    RRHH=self.RRHH
    informacionBolsa=self.informacionBolsa
    nuevoEmpleado=self.nuevoEmpleado
    nuevoCliente=self.nuevoCliente
    nuevoProveedor=self.nuevoProveedor
    bar = self.menuBar()

    #Añadiendo ventanas hijas
    mdiArea.addSubWindow(login)
    mdiArea.addSubWindow(compras)
    mdiArea.addSubWindow(ventas)
    mdiArea.addSubWindow(RRHH)
    mdiArea.addSubWindow(informacionBolsa)

    #Añadiendo menus
    #Menu Cuenta
    cuenta=bar.addMenu("Cuenta")
    cuenta.addAction("Cerrar Sesion")

    #Menu Opcion
    opcion = bar.addMenu("Opcion")
    opcion.addAction("Compras")
    opcion.addAction("Ventas")
    opcion.addAction("RRHH")
    opcion.addAction("Bolsa de Valores")

    #Iniciando Presentación
    self.setCentralWidget(mdiArea)
    login.showMaximized()
    compras.close()
    compraDetalle.close()
    ventas.close()
    ventaDetalle.close()
    RRHH.close()
    informacionBolsa.close()
    nuevoEmpleado.close()
    nuevoCliente.close()
    nuevoProveedor.close()

    #Conexiones
    login.opcion.accepted.connect(self.verificarCuenta)
    login.opcion.rejected.connect(QCoreApplication.quit)

    compras.agregarCompra.clicked.connect(self.iniciarDetalleCompra)

    compraDetalle.agregarProducto.clicked.connect(self.aniadirProductoCompra)
    compraDetalle.confirmarCompra.accepted.connect(self.aniadirCompra)
    compraDetalle.confirmarCompra.rejected.connect(self.cerrarCompraDetalle)

    ventas.agregarVenta.clicked.connect(self.iniciarDetalleVenta)
    ventas.agregarCliente.clicked.connect(self.iniciarAgregarCliente)
    ventas.actualizar.clicked.connect(self.iniciarVenta)

    compras.nuevoProveedor.clicked.connect(self.iniciarAgregarProveedor)

    ventaDetalle.agregarProducto.clicked.connect(self.aniadirProductoVenta)
    ventaDetalle.confirmarVenta.accepted.connect(self.aniadirVenta)
    ventaDetalle.confirmarVenta.rejected.connect(self.cerrarVentaDetalle)

    cuenta.triggered[QAction].connect(self.cuentaAction)
    opcion.triggered[QAction].connect(self.opcionAction)

    informacionBolsa.actualizar.clicked.connect(self.iniciarBV)

    self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)
    RRHH.agregarEmpleado.clicked.connect(self.aniadirEmpleado)

    nuevoEmpleado.confirmarEmpleado.accepted.connect(self.guardarEmpleado)
    nuevoEmpleado.confirmarEmpleado.rejected.connect(self.cerrarAgregarEmpleado)

    nuevoCliente.confirmarCliente.accepted.connect(self.guardarCliente)
    nuevoCliente.confirmarCliente.rejected.connect(self.cerrarAgregarCliente)

    nuevoProveedor.confirmarProveedor.accepted.connect(self.guardarProveedor)
    nuevoProveedor.confirmarProveedor.rejected.connect(self.cerrarAgregarProveedor)
  
  def guardarClienteBD(self,ID,nombre,RUC):
    try:
      self.cur.execute("insert into cliente values("+str(ID)+",'"+nombre+"','"+RUC+"')")
      self.conn.commit()
    except:
      self.conn.rollback()

  def guardarProveedorBD(self,ID,nombre,RUC):
    try:
      self.cur.execute("insert into distribuidor values("+str(ID)+",'"+nombre+"','"+RUC+"')")
      self.conn.commit()
    except:
      self.conn.rollback()

  def guardarCliente(self):
    self.nuevoCliente.IDultimoCliente +=1
    ID = self.nuevoCliente.IDultimoCliente
    nombre=self.nuevoCliente.nombre.text()
    RUC = self.nuevoCliente.RUC.text()
    self.guardarClienteBD(ID,nombre,RUC)
    self.cerrarAgregarCliente()

  def guardarProveedor(self):
    self.nuevoProveedor.IDultimoProveedor+=1
    ID = self.nuevoProveedor.IDultimoProveedor
    nombre=self.nuevoProveedor.nombre.text()
    RUC = self.nuevoProveedor.RUC.text()
    self.guardarProveedorBD(ID,nombre,RUC)
    self.cerrarAgregarProveedor()


  def guardarEmpleadoBD(self,ID,nombre,DNI,puesto,sueldo):
    try:
      self.cur.execute("insert into empleados values(" +str(ID)+" ,'"+nombre+"' , '"+DNI+"' , "+puesto+" ,'"+str(sueldo)+"')")
      self.conn.commit()
    except:
      self.conn.rollback()

  def guardarEmpleado(self):
    self.RRHH.IDultimoEmpleado+=1
    ID = self.RRHH.IDultimoEmpleado
    nombre=self.nuevoEmpleado.nombre.text()
    DNI = self.nuevoEmpleado.dni.text()
    puesto = self.nuevoEmpleado.puesto.currentText()
    sueldo = self.nuevoEmpleado.salario.value()
    self.guardarEmpleadoBD(ID,nombre,DNI,puesto,sueldo)
    itemEmpleado=[str(ID),nombre,puesto]
    RRHH=self.RRHH
    posRow=RRHH.listEmpleados.rowCount();
    RRHH.listEmpleados.insertRow(posRow)
    for j in range (len(itemEmpleado)):
      item=QTableWidgetItem(str(itemEmpleado[j]))
      RRHH.listEmpleados.setItem(posRow,j,item)
    self.cerrarAgregarEmpleado()

  def cerrarAgregarEmpleado(self):
    self.nuevoEmpleado.close()

  def iniciarAgregarCliente(self):
    self.nuevoCliente.show()

  def iniciarAgregarProveedor(self):
    self.nuevoProveedor.show()

  def cerrarAgregarCliente(self):
    self.nuevoCliente.close()

  def cerrarAgregarProveedor(self):
    self.nuevoProveedor.close()

  def idCliente(self,cliente):
    print (cliente)
    self.cur.execute("select ID from cliente where nombre='"+cliente+"'")
    result=self.cur.fetchall()
    for i in result:
      return i[0]
    return None

  def aniadirVenta(self):
    cliente=self.ventaDetalle.clientes.currentText()
    IDcliente=self.idCliente(cliente)
    fecha=self.ventaDetalle.fecha.date()
    fecha=str(fecha.year())+"-"+str(fecha.month())+"-"+str(fecha.day())
    if (IDcliente!=None):
      self.ventas.IDultimaVenta+=1
      ID = self.ventas.IDultimaVenta
      ejecutar="insert into ventas values("+str(ID)+","+str(IDcliente)+",'"+fecha+"')"
      self.cur.execute(ejecutar)
      self.conn.commit()
      self.cerrarVentaDetalle()
      return
    print ("No existe Cliente-Si es nuevo Cliente Agregelo en Ventas")

  def aniadirCompra(self):
    print ()

  #Consultando el ultimo ID de una tabla
  def ultimoID(self,tabla):
    self.cur.execute("select MAX(ID) from "+tabla)
    results=self.cur.fetchall()
    if(results[0][0]!=None):
      return results[0][0]
    else:
      return 0

  #Iniciando Bolsa de Valores
  def iniciarBV(self):
    self.login.Notificacion.setText("Actualizando ...")
    iBolsa=self.iBolsa
    iBolsa.actualizarDatos()
    inicio=0
    while not iBolsa.tweets.empty():
      item=QStandardItem(iBolsa.tweets.get().tweet.text)
      model=self.informacionBolsa.model
      model.appendRow(item)
      if (inicio%2==0):
        model.setData(model.index(inicio,0),Qt.blue,Qt.yellow)
      inicio+=1
    self.informacionBolsa.listView.setModel(model)
    self.login.Notificacion.setText("")

  #Iniciando Venta
  def iniciarVenta(self):
    r = urllib.request.urlopen("http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias")
    self.soup = BeautifulSoup(r,"html.parser")
    self.data = []
    table = self.soup.find("table",{"class": "class=\"form-table\""})
    rows= table.findAll("tr");
    for row in rows:
      cols = row.findAll ("td")
      cols = [ele.text.strip() for ele in cols]
      self.data.append([ele for ele in cols if ele])
    titles=["Día","Compra","Venta"]
    self.ventas.tipoDeCambio.setRowCount(3)
    self.ventas.tipoDeCambio.horizontalHeader().setVisible(False);
    self.ventas.tipoDeCambio.setVerticalHeaderLabels(titles)
    print (self.data)
    for j in range (3):
      self.ventas.tipoDeCambio.insertColumn(j)
      for k in range (3):
        item=QTableWidgetItem(str(self.data[len(self.data)-1][j*3+k]))
        self.ventas.tipoDeCambio.setItem(k,2-j,item)

  #Iniciando Recursos Humanos
  def iniciarRRHH(self):
    RRHH=self.RRHH
    while (RRHH.listEmpleados.rowCount() > 0):
      RRHH.listEmpleados.removeRow(0);
    RRHH.listEmpleados.setColumnCount(3)
    RRHH.listEmpleados.setHorizontalHeaderLabels(self.titlesEmpleado)
    self.cur.execute("select *from empleados")
    self.resultEmpleados=self.cur.fetchall()
    resultEmpleados=self.resultEmpleados
    for i in range (len(resultEmpleados)):
      emp=resultEmpleados[i]
      itemEmpleado=[str(emp[0]),emp[1],emp[3]]
      RRHH.listEmpleados.insertRow(i)
      for j in range (len(itemEmpleado)):
        item=QTableWidgetItem(str(itemEmpleado[j]))
        RRHH.listEmpleados.setItem(i,j,item)

  #Iniciando una venta
  def iniciarDetalleVenta(self):
    listProductos=[]
    self.cur.execute("select nombre from productos")
    results=self.cur.fetchall()
    for i in range (len(results)):
      listProductos+=[results[i][0]]
    self.ventaDetalle.productos.addItems(listProductos)
    self.ventaDetalle.show()

  #Iniciando una compra
  def iniciarDetalleCompra(self):
    self.compras.IDultimaCompra+=1
    listProductos=[]
    self.cur.execute("select nombre from productos")
    results=self.cur.fetchall()
    for i in range (len(results)):
      listProductos+=[results[i][0]]
    self.compraDetalle.productos.addItems(listProductos)
    self.compraDetalle.show()

  #Verificar Administrador en Base de Datos
  def verificarAdministrador(self,usuario,contrasenia):
    self.cur.execute("select ID from administrador where usuario='"+usuario+"'and contrasenia='"+contrasenia+"' ")
    results=self.cur.fetchall()
    if len(results)>0:
      return results[0][0]
    else:
      return None

  #Añadir producto de una venta
  def aniadirProductoVenta(self):
    ventaDetalle=self.ventaDetalle
    product_name=ventaDetalle.productos.currentText()
    cantidad=ventaDetalle.cantidadProducto.value()
    self.cur.execute("select ID,precio from productos where nombre='"+product_name+"'")
    results=self.cur.fetchall()
    productosVenta=ventaDetalle.productosVenta
    numberRow=productosVenta.rowCount()
    productosVenta.insertRow(numberRow)
    newRow=[results[0][0],product_name,results[0][1],cantidad]
    for i in range (len(newRow)):
      item=QTableWidgetItem(str(newRow[i]))
      productosVenta.setItem(numberRow,i,item)

  def aniadirProductoCompra(self):
    compraDetalle=self.compraDetalle
    product_name=compraDetalle.productos.currentText()
    cantidad=compraDetalle.cantidadProducto.value()
    precio=compraDetalle.precioProducto.value()
    self.cur.execute("select ID,precio from productos where nombre='"+product_name+"'")
    results=self.cur.fetchall()
    productosCompra=compraDetalle.productosCompra
    numberRow=productosCompra.rowCount()
    productosCompra.insertRow(numberRow)
    newRow=[results[0][0],product_name,precio,cantidad]
    for i in range (len(newRow)):
      item=QTableWidgetItem(str(newRow[i]))
      productosCompra.setItem(numberRow,i,item)

  def aniadirEmpleado(self):
    self.nuevoEmpleado.show()

  #Verificando la cuenta ingresada en login
  def verificarCuenta(self):
    login=self.login
    usuario_ing=login.usuario.currentText()
    contrasenia_ing=login.contrasenia.text()
    ID= self.verificarAdministrador(usuario_ing,contrasenia_ing);
    if ID==None:
      login.Notificacion.setText("Usuario o contraseña incorrecta")
    else:
      self.administradorActive=ID
      self.iniciarServicio()

  #Iniciar el servicio tras haber verificado la cuenta
  def iniciarServicio(self):
    if(self.administradorActive!=None):
      self.login.Notificacion.setText("Iniciando Servicio")
      self.compraDetalle.productosCompra.setColumnCount(4)
      self.compraDetalle.productosCompra.setHorizontalHeaderLabels(self.titlesProducto)
      self.ventaDetalle.productosVenta.setColumnCount(4)
      self.ventaDetalle.productosVenta.setHorizontalHeaderLabels(self.titlesProducto)
      self.login.Notificacion.setText("Iniciando RRHH-Ventas-Compras")
      self.iniciarRRHH()
      #self.iniciarVenta()
      self.ventas.IDultimaVenta=self.ultimoID("ventas")
      self.compras.IDultimaCompra=self.ultimoID("compras")
      self.nuevoCliente.IDultimoCliente=self.ultimoID("cliente")
      self.nuevoProveedor.IDultimoProveedor=self.ultimoID("distribuidor")
      self.RRHH.IDultimoEmpleado=self.ultimoID("empleados")
      self.login.Notificacion.setText("Actualizando Noticias")
      #self.iniciarBV()
      self.login.Notificacion.setText("")
      self.showMaximized()
      self.login.close()
      for win in self.mdiArea.subWindowList():
        if win.accessibleName()!="login":
          win.show()
      self.mdiArea.tileSubWindows()

  #Retornar ventanas hija activa. No usado pero necesario si usamos multiWindow para un tipo de ventana dentro del MDI, ademas de facil implementación
  def activeMdiChild(self):
    activeSubWindow = self.mdiArea.activeSubWindow()
    if activeSubWindow:
      return activeSubWindow.widget()
    return None

  #Activar ventana hija. No usado.
  def setActiveSubWindow(self,window):
    if window:
      self.mdiArea.setActiveSubWindow(window)

  #Acciones de menu Cuenta
  def cuentaAction(self, q):
    if self.administradorActive!=0:
      if q.text() == "Cerrar Sesion":
        RRHH=self.RRHH
        while (RRHH.listEmpleados.rowCount() > 0):
          RRHH.listEmpleados.removeRow(0);
        self.administradorActive=None
        self.compras.close()
        self.ventas.close()
        self.RRHH.close()
        self.showNormal()
        self.login.show()

  #Accionones de menu Opcion
  def opcionAction(self, q):
    if self.administradorActive!=0:
      if q.text() == "Compras":
        self.compras.close()
        self.compras.show()
      if q.text() == "Ventas":
        self.ventas.close()
        self.ventas.show()
      if q.text() == "RRHH":
        self.RRHH.close()
        self.RRHH.show()
      if q.text() == "Bolsa de Valores":
        self.informacionBolsa.close()
        self.informacionBolsa.show()

  def cerrarVentaDetalle(self):
    self.ventaDetalle.close()

  def cerrarCompraDetalle(self):
    self.compraDetalle.close()

def main():
  app = QApplication(sys.argv)
  ex = MainWindow()
  ex.show()
  sys.exit(app.exec_())

if __name__=='__main__':
  sys.exit(main())
