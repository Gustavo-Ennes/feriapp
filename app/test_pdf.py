from pdf import PDF
import sys, traceback

def __main__():
	try:
		PDF.create_basic_pdf()
	except Exception as e:
		print("Exception in user code:")
		print('-'*60)
		traceback.print_exc(file=sys.stdout)
		print('-'*60)
		return
	finally:
		print("O pdf foi atualizado")

__main__()
