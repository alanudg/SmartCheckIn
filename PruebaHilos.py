 i m p o r t   t h r e a d i n g 
 i m p o r t   t i m e 
 d e f   f i n i s h ( ) : 
         p r i n t   t h r e a d i n g . c u r r e n t T h r e a d ( ) . g e t N a m e ( ) ,   ' L a n z a d o ' 
         t i m e . s l e e p ( 2 ) 
         p r i n t   t h r e a d i n g . c u r r e n t T h r e a d ( ) . g e t N a m e ( ) ,   ' D e t e n i e n d o ' 
 d e f   s t a r t ( ) : 
         p r i n t   t h r e a d i n g . c u r r e n t T h r e a d ( ) . g e t N a m e ( ) ,   ' L a n z a d o ' 
         p r i n t   t h r e a d i n g . c u r r e n t T h r e a d ( ) . g e t N a m e ( ) ,   ' D e t e n i e n d o ' 
 t   =   t h r e a d i n g . T h r e a d ( t a r g e t = f i n i s h ,   n a m e = ' F i n i s h ' ) 
 w   =   t h r e a d i n g . T h r e a d ( t a r g e t = s t a r t ,   n a m e = ' S t a r t ' ) 
 t . s t a r t ( ) 
 w . s t a r t ( ) 
