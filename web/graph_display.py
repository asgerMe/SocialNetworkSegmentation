import numpy as np
import pickle
import os
from pathlib import Path

class GraphDisplay():
    def __init__(self, graph=None, rotatex = 0, rotatey = 0, rotatez = 0):

        self.graph = graph
        self.height = 500
        self.width = 500

        self.center = [self.width/2, self.width/2, 0]
        self.x0 = [-self.width, 0, 0]
        self.x1 = [self.width, 0, 0]

        self.y0 = [0, -self.width, 0]
        self.y1 = [0, self.width, 0]

        self.z0 = [0, 0, -self.width]
        self.z1 = [0, 0, self.width]

        self.rotation_matrix(rotatex, rotatey, rotatez)

    def rotation_matrix(self, xdeg=0.0, ydeg=0.0, zdeg=0.0):
        xrad = xdeg * np.pi / 180
        yrad = ydeg * np.pi / 180
        zrad = zdeg * np.pi / 180

        rotate_x = np.asmatrix([[1, 0, 0], [0, np.cos(xrad), -np.sin(xrad)], [0, np.sin(xrad), np.cos(xrad)]])
        rotate_y = np.asmatrix([[np.cos(yrad), 0, np.sin(yrad)], [0, 1, 0], [-np.sin(yrad), 0, np.cos(yrad)]])
        rotate_z = np.asmatrix([[np.cos(zrad), -np.sin(zrad), 0], [np.sin(zrad), np.cos(zrad), 0], [0, 0, 1]])

        R = rotate_z*rotate_y*rotate_x

        self.x0 = np.asarray(self.center + self.x0*R)[0]
        self.x1 = np.asarray(self.center + self.x1*R)[0]

        self.y0 = np.asarray(self.center + self.y0*R)[0]
        self.y1 = np.asarray(self.center + self.y1*R)[0]

        self.z0 = np.asarray(self.center + self.z0*R)[0]
        self.z1 = np.asarray(self.center + self.z1*R)[0]

    def create_xaxis(self):
        return '''
            ctx.beginPath();
            var gradx = ctx.createLinearGradient({}, {}, {}, {});
            gradx.addColorStop(0, "transparent");
            gradx.addColorStop({}, "grey");
            ctx.strokeStyle = gradx;
            ctx.moveTo({}, {});
            ctx.lineTo({}, {});
            ctx.lineWidth = 3;
            ctx.stroke();
        '''.format(self.x0[0], self.x0[1], self.x1[0], self.x1[1], abs(self.x0[2]/self.width), self.x0[0], self.x0[1], self.x1[0], self.x1[1])

    def create_yaxis(self):
        return '''
             ctx.beginPath();
             var grady= ctx.createLinearGradient({}, {}, {}, {});
             grady.addColorStop(0, "transparent");
             grady.addColorStop({}, "grey");
             ctx.strokeStyle = grady;
             ctx.moveTo({}, {});
             ctx.lineTo({}, {});
             ctx.stroke();
         '''.format(self.y0[0], self.y0[1], self.y1[0], self.y1[1], abs(self.y0[2]/self.width), self.y0[0], self.y0[1], self.y1[0], self.y1[1])

    def create_zaxis(self):
        return '''
            ctx.beginPath();
            var gradz= ctx.createLinearGradient({}, {}, {}, {});
            gradz.addColorStop(0, "transparent");
            gradz.addColorStop({}, "grey");

            ctx.strokeStyle = gradz;
            ctx.moveTo({}, {});
            ctx.lineTo({}, {});
            ctx.stroke();
         '''.format(self.z0[0], self.z0[1], self.z1[0], self.z1[1], abs(self.z0[2]/self.width), self.z0[0], self.z0[1], self.z1[0], self.z1[1])

    def create_nodes(self):
        return 0
    
    def script(self):
        return """<script>
                    var c = document.getElementById("myCanvas");
                    var ctx = c.getContext("2d");
                    // Create gradient
                    var grd = ctx.createLinearGradient(0,0,0,{});
                    grd.addColorStop(0,"white");
                    grd.addColorStop(1,"white");
                    // Fill with gradient
                    ctx.fillStyle = grd;
                    ctx.fillRect(0,0,{},{});
                    
                    {}
                    {}
                    {}
                  
        </script>""".format(
                            self.height,
                            self.width,
                            self.height,
                            self.create_xaxis(),
                            self.create_yaxis(),
                            self.create_zaxis()
                            )

    def canvas(self):
        return '<canvas style="padding-top: 10px;" id="myCanvas" width={}; height={};>'.format(self.width, self.height)