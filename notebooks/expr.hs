data Expr = Add Expr Expr
          | Mul Expr Expr
          | Val Float
          

expr1 = Add (Val 1) (Val 2.5)

expr2 = Add (Mul (Val 2) (Val 7.5)) (Val 3)

eval :: Expr -> Float
eval (Add a b) = (eval a) + (eval b)
eval (Mul a b) = (eval a) * (eval b)
eval (Val a) = a

postfix :: Expr -> String
postfix (Add a b) = (postfix a) ++ (postfix b) ++ " + "
postfix (Mul a b) = (postfix a) ++ (postfix b) ++ " * "
postfix (Val a) = show a ++ " "

type Point = (Float, Float)

data Fig = Circle Point Float
         | Rect Point Float Float
         | Text Point String
         | Line Point Point
         | Grp Point [Fig]
         
fig1 = Circle (10, 10) 20

tosvg :: Fig -> String
tosvg (Circle (mx, my) r) = "<circle x=" ++ (show mx) ++ " y=" ++ (show my) ++ " r=" ++ (show r) ++ " /> \n"
tosvg (Rect (mx, my) w h) = "<rect x=" ++ (show mx) ++ " y=" ++ (show my) ++ " w=" ++ (show w) ++ " h=" ++ (show h) ++ " />"
tosvg (Text (mx, my) s) = "<text x=" ++ (show mx) ++ " y=" ++ (show my) ++ ">" ++ s ++ "</text>"
tosvg (Line (ax, ay) (bx, by)) = "<line x1=" ++ (show ax) ++ " y1=" ++ (show ay) ++ "x2=" ++ (show bx) ++ " y2=" ++ (show by) ++ "/> \n "
tosvg (Grp (mx, my) lst) = "<g transform=\"translate(" ++ (show mx) ++ " " ++ (show my) ++ ")\" > \n" ++ elems ++ "</g>\n"
                           where svg_lst = map tosvg lst
                                 elems = foldr (++) "" svg_lst
                                
fig4 = Line (10, 10) (100, 100)
fig3 = Grp (10, 20) [fig1, Grp (30, 40) [fig1], fig4]
                                

foldrx :: (a -> b -> b) -> b -> [a] -> b
foldrx f y [] = y
foldrx f y (x:xs) = f x (foldrx f y xs)

data Tree a = Nil | Node a (Tree a) (Tree a) deriving (Show)

tmap :: (a -> b) -> (Tree a) -> (Tree b)
tmap f Nil = Nil
tmap f (Node x lt rt) = Node (f x) (tmap f lt) (tmap f rt)

tree1 = Node 1 (Node 2 Nil Nil) (Node 3 (Node 4 Nil Nil) Nil)


         