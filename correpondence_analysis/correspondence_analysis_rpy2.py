import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
made4r = importr("made4r")
distEisen = robjects.r('''
                       distEisen <- function(x, use = "pairwise.complete.obs") {
                       co.x <- cor(x, use = use)
                       dist.co.x <- 1 - co.x
                       return(as.dist(dist.co.x))
                       }
                       ''')

listToDF = robjects.r('''
           listToDF <- function(inputList, fill = NA){
               # Use fill = NULL for regular recycling behavior
               maxLen = max(sapply(inputList, length))
               for(i in seq_along(inputList))
                   inputList[[i]] <- c(inputList[[i]], rep(fill, maxLen -
           length(inputList[[i]])))
               return(as.data.frame(inputList))
           }
           ''')
annotations = DataFrame.from_csvfile(annotation_classes_input_file,
                                     header=True,
                                     sep='\t',
                                     quote='"',
                                     row_names=1)


R = robjects.r
R["library"]("utils")
R["library"]("tools")


