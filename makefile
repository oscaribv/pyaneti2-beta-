#-------------------------------------------------------------------------#
#                         Makefile for pyaneti                            #
#                       Oscar Barragán, Oct. 2016                         #
#-------------------------------------------------------------------------#
#    make       -> compiles the code in its sequential configuration      #
#    make para  -> compiles the code in its parallel configuration        #
#    make clean -> removes the pyaneti.so file                            #
#-------------------------------------------------------------------------#

FP=f2py3.6
#FP=f2py2.7
fc=gnu95 
cc=unix 

FLAGS_OMP= -c -m --quiet --f90flags='-fopenmp'
FLAGS= -c -m  --quiet
BLIBS = -L/usr/lib/x86_64-linux-gnu/ -llapack -lblas
LGOMP=-L/usr/lib64/ -lgomp

SOURCES=src/constants.f90\
	src/todo.f90\
	src/qpower2.f90\
	src/quad.f90\
        src/ftr.f90\
	src/frv.f90\
	src/bayesian.f90\
	src/matrices.f90\
	src/kernels.f90\
	src/mcmc.f90\
	src/multi-kernel.f90\

EXECUTABLE=pyaneti

all: $(EXECUTABLE) 
%.mod: %.90
	$(FC) -c $(SOURCES)
$(EXECUTABLE):$(SOURCES)
	${FP} ${FLAGS} $(EXECUTABLE) $(SOURCES)  --fcompiler=$(fc) ${BLIBS} --compiler=$(cc)


para: $(EXECUTABLE)
	${FP} ${FLAGS_OMP} $(EXECUTABLE) $(SOURCES)  --fcompiler=$(fc) ${BLIBS} ${LGOMP}  --compiler=$(cc)

clean:
	rm *.so src/*.mod src/*.o
