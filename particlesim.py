import math, random, Tkinter as tk

def sigfigify (number, figs):
    if number == 0:
        return 0
    else:
        return round(number, -int(math.floor(math.log10(abs(number))) - figs + 1))

class MyTk (tk.Tk):

    def __init__ (self):
        tk.Tk.__init__(self)

        self.option_add("*Font", ("Calibri", 13))

    def center (self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2) - 30
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

class MyEntry (tk.Entry):

    def __init__ (self, master, **kwargs):
        tk.Entry.__init__(self, master, width=10, **kwargs)

    def set (self, string):
        self.delete(0, tk.END)
        self.insert(0, string)



class Particle:
    
    def __init__ (self, parent, mass = 1, pos = [0,0], vel = [0,0]):
        self.parent = parent
        self.mass = mass # kilograms
        self.pos = pos # meters
        self.vel = vel # meters per second

        self.init_mass = mass
        self.init_pos = [pos[0], pos[1]]
        self.init_vel = [vel[0], vel[1]]

        # radii of particles on screen should average to 10 pixels and be proportional to mass
        self.radius = self.mass * self.parent.particle_avgradius / self.parent.avgmass

        self.drawing = self.parent.canvas.create_oval(0, 0, 2 * self.radius, 2 * self.radius)
        self.drawing_arrow_vel = self.parent.canvas.create_line(0, 0, 30, 0, arrow=tk.LAST, fill="#0000FF")
        self.drawing_arrow_accel = self.parent.canvas.create_line(0, 0, 30, 0, arrow=tk.LAST, fill="#FF0000")
        
        self.parent.canvas.itemconfigure(self.drawing, offset = tk.CENTER)

    def __repr__ (self):
        return str(self.parent.particles.index(self) + 1) + " (" + str(sigfigify(self.init_mass, 3)) + " kg)"

class App (MyTk):

    def __init__ (self, scale=0.01, gravity=6.67e-11, timeincrement=0.01, targetfps=100):
        MyTk.__init__(self)

        self.scale = scale # scale of projection in meters per pixel
        self.gravity = gravity # in cubic meters per kilogram square second
        self.timeincrement = timeincrement # how much virtual time is increased every frame in seconds
        self.targetfps = targetfps # target frames per second for simulation

        self.avgmass = pow(self.scale, 3) / self.gravity * pow(10, 8) # average mass of particles in kilograms
        self.massvariation = 1.0 # variation in masses of particles (see add_particle() for details)
        self.particle_avgradius = 10.0 # average radius of particles on screen
        self.bounds_radius = 300 # half the width/height of the screen (particles are bound to the screen)
        
        self.wm_title("ParticleSim")

        self.canvas = tk.Canvas(self, width = 2 * self.bounds_radius, height = 2 * self.bounds_radius, background="#FFFFFF")
        self.canvas.grid(column=0, row=0, rowspan=4)

        # axes
        
        self.canvas.create_line(0, self.bounds_radius, 2 * self.bounds_radius, self.bounds_radius)
        self.canvas.create_line(self.bounds_radius, 0, self.bounds_radius, 2 * self.bounds_radius)

        self.texts_x_axis = []
        self.texts_y_axis = []
        
        for i in range(1, 6):
            self.canvas.create_line(i * self.bounds_radius / 3, self.bounds_radius - 10, i * self.bounds_radius / 3, self.bounds_radius + 10)
            self.canvas.create_line(self.bounds_radius - 10, i * self.bounds_radius / 3, self.bounds_radius + 10, i * self.bounds_radius / 3)

            if i != 3:
                text_x_axis = self.canvas.create_text(i * self.bounds_radius / 3, self.bounds_radius - 25, text = str(sigfigify((i - 3) * scale * 100, 1)), font = "Calibri 12")
                self.texts_x_axis.append(text_x_axis)
                
                text_y_axis = self.canvas.create_text(self.bounds_radius + 15, i * self.bounds_radius / 3, text = str(sigfigify((i - 3) * scale * 100, 1)), font = "Calibri 12", anchor = tk.W)
                self.texts_y_axis.append(text_y_axis)

        # settings panes

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.frame_timecontrols = tk.Frame(self, borderwidth=1, relief=tk.RIDGE)
        self.frame_timecontrols.grid(column=1, row=0, sticky="NEWS")
        self.frame_timecontrols.grid_columnconfigure(0, weight=1)

        self.label_time = tk.Label(self.frame_timecontrols, text="Time", font="Calibri 16 bold")
        self.label_time.grid(column=0, row=0, sticky="NEWS")

        self.frame_timecontrols_buttons = tk.Frame(self.frame_timecontrols)
        self.frame_timecontrols_buttons.grid(column=0, row=1)

        self.button_prev = tk.Button(self.frame_timecontrols_buttons, text=u"\u23EA", command=self.prev)
        self.button_prev.grid(column=0, row=1)
        
        self.button_playpause = tk.Button(self.frame_timecontrols_buttons, text=u"\u25B6", command=self.playpause)
        self.button_playpause.grid(column=1, row=1)

        self.button_start = tk.Button(self.frame_timecontrols_buttons, text=u"\u25FC", command=self.stop)
        self.button_start.grid(column=2, row=1)

        self.button_next = tk.Button(self.frame_timecontrols_buttons, text=U"\u23E9", command=self.next)
        self.button_next.grid(column=3, row=1)

        self.frame_particles = tk.Frame(self, borderwidth=1, relief=tk.RIDGE)
        self.frame_particles.grid(column=1, row=1, sticky="NEWS")
        self.frame_particles.grid_columnconfigure(0, weight=1)
        self.frame_particles.grid_columnconfigure(1, weight=1)

        self.label_particles = tk.Label(self.frame_particles, text="Particles", font="Calibri 16 bold")
        self.label_particles.grid(column=0, row=0, columnspan=2)

        self.frame_listbox_particles = tk.Frame(self.frame_particles)
        self.frame_listbox_particles.grid(column=0, row=1, columnspan=2)

        self.listbox_particles_vscroll = tk.Scrollbar(self.frame_listbox_particles, orient=tk.VERTICAL)
        self.listbox_particles_vscroll.grid(column=1, row=0, sticky="NEWS")

        self.listbox_particles = tk.Listbox(self.frame_listbox_particles, height=5,
                                            yscrollcommand=self.listbox_particles_vscroll.set)
        self.listbox_particles.grid(column=0, row=0, sticky="NEWS")
        self.listbox_particles_vscroll['command'] = self.listbox_particles.yview

        self.button_add_particle = tk.Button(self.frame_particles, text="Add Particle...", command=self.add_particle)
        self.button_add_particle.grid(column=0, row=2, columnspan=2)

        self.button_add_random_particle = tk.Button(self.frame_particles, text="Add Random Particle", command=self.add_random_particle)
        self.button_add_random_particle.grid(column=0, row=3, columnspan=2)

        self.button_delete_particle = tk.Button(self.frame_particles, text="Delete Particle", command=self.delete_particle)
        self.button_delete_particle.grid(column=0, row=4, columnspan=2)

        self.frame_settings = tk.Frame(self, borderwidth=1, relief=tk.RIDGE)
        self.frame_settings.grid(column=1, row=2, sticky="NEWS")

        self.label_settings = tk.Label(self.frame_settings, text="Settings", font="Calibri 16 bold")
        self.label_settings.grid(column=2, row=1, columnspan=2)

        self.label_scale = tk.Label(self.frame_settings, text="Scale (m/px):")
        self.label_scale.grid(column=2, row=2)

        self.entry_scale = MyEntry(self.frame_settings)
        self.entry_scale.grid(column=3, row=2)

        self.label_gravity = tk.Label(self.frame_settings, text="Gravity (m" + u"\u00B3" + "/kgs" + u"\u00B2" + "):")
        self.label_gravity.grid(column=2, row=3)

        self.entry_gravity = MyEntry(self.frame_settings)
        self.entry_gravity.grid(column=3, row=3)

        self.label_timeincrement = tk.Label(self.frame_settings, text="Time Increment (s):")
        self.label_timeincrement.grid(column=2, row=4)

        self.entry_timeincrement = MyEntry(self.frame_settings)
        self.entry_timeincrement.grid(column=3, row=4)

        self.label_targetfps = tk.Label(self.frame_settings, text="Target FPS:")
        self.label_targetfps.grid(column=2, row=5)

        self.entry_targetfps = MyEntry(self.frame_settings)
        self.entry_targetfps.grid(column=3, row=5)

        self.button_update_settings = tk.Button(self.frame_settings, text="Update", command=self.update_settings)
        self.button_update_settings.grid(column=2, row=6, columnspan=2)

        self.label_author = tk.Label(self, text="Made by hPerks\nSeptember 29, 2015")
        self.label_author.grid(column=1, row=3)

        self.center()

        self.fill_settings()

        self.particles = []
        for i in range(4):
            self.add_random_particle()

        self.isrunning = False
        self.start_simulation()
        self.after(1000/self.targetfps, self.update)

    def start_simulation (self):
        self.time = 0
        for particle in self.particles:
            particle.pos = [particle.init_pos[0], particle.init_pos[1]]
            particle.vel = [particle.init_vel[0], particle.init_vel[1]]

    def fill_settings(self):
        self.entry_scale.set(str(self.scale))
        self.entry_gravity.set(str(self.gravity))
        self.entry_timeincrement.set(str(self.timeincrement))
        self.entry_targetfps.set(str(self.targetfps))

    def update_settings(self):

        # make sure entries are valid floats/ints
        try:
            self.gravity = float(self.entry_gravity.get())
            self.timeincrement = float(self.entry_timeincrement.get())
            self.targetfps = int(self.entry_targetfps.get())

            # we can't update this setting yet, because we need to compare it with the old value
            new_scale = float(self.entry_scale.get())
            
        except ValueError:
            pass
                
        finally:

            # update axis labels
            for text in self.texts_x_axis + self.texts_y_axis:
                self.canvas.itemconfig(text, text = sigfigify(float(self.canvas.itemcget(text, "text")) * new_scale / self.scale, 1))

            # now we can update this setting
            self.scale = new_scale

            self.avgmass = abs(pow(self.scale, 3) / self.gravity * pow(10, 8))

        self.fill_settings()
        
    def add_random_particle(self):
        
        # if the average mass is a and the mass variation is v, the natural logs of the masses range uniformly from (lna - v) to (lna + v)
        mass = pow(pow(math.e, self.massvariation), (random.random() * 2 - 1)) * self.avgmass

        posx = (random.random() * 2 - 1) * self.scale * self.bounds_radius
        posy = (random.random() * 2 - 1) * self.scale * self.bounds_radius

        # velocity can be in any direction, and speed can range from 1 to 2 times a third of the screen size
        direction = random.random() * 2 * math.pi
        speed = (random.random() + 1) * self.scale * self.bounds_radius / 3
        velx = speed * math.cos(direction)
        vely = speed * math.sin(direction)

        self.particles.append(Particle(parent = self, mass = mass, pos = [posx, posy], vel = [velx, vely]))
        self.update_particles_listbox()

    def add_particle(self):
        
        self.window_add_particle = MyTk()
        self.window_add_particle.wm_title("Add Particle")

        self.label_particle_mass = tk.Label(self.window_add_particle, text="Mass (kg):")
        self.label_particle_mass.grid(row=1, column=0)

        self.entry_particle_mass = MyEntry(self.window_add_particle)
        self.entry_particle_mass.grid(row=1, column=1, columnspan=3)

        self.label_particle_position = tk.Label(self.window_add_particle, text="Position (m):")
        self.label_particle_position.grid(row=2, column=0)

        self.entry_particle_position_x = MyEntry(self.window_add_particle)
        self.entry_particle_position_x.grid(row=2, column=1)

        self.label_particle_position_comma = tk.Label(self.window_add_particle, text=",")
        self.label_particle_position_comma.grid(row=2, column=2)

        self.entry_particle_position_y = MyEntry(self.window_add_particle)
        self.entry_particle_position_y.grid(row=2, column=3)

        self.label_particle_velocity = tk.Label(self.window_add_particle, text="Velocity (m/s):")
        self.label_particle_velocity.grid(row=3, column=0)

        self.entry_particle_velocity_x = MyEntry(self.window_add_particle)
        self.entry_particle_velocity_x.grid(row=3, column=1)

        self.label_particle_velocity_comma = tk.Label(self.window_add_particle, text=",")
        self.label_particle_velocity_comma.grid(row=3, column=2)

        self.entry_particle_velocity_y = MyEntry(self.window_add_particle)
        self.entry_particle_velocity_y.grid(row=3, column=3)

        self.button_add_particle_ok = tk.Button(self.window_add_particle, text="OK", command=self.add_particle_ok)
        self.button_add_particle_ok.grid(row=4, column=0, columnspan=4)

        self.window_add_particle.center()

    def add_particle_ok(self):
        try:
            mass = float(self.entry_particle_mass.get())
            pos = [float(self.entry_particle_position_x.get()),
                   float(self.entry_particle_position_y.get())]
            vel = [float(self.entry_particle_velocity_x.get()),
                   float(self.entry_particle_velocity_y.get())]

        except:
            pass

        finally:
            self.particles.append(Particle(self, mass, pos, vel))
            self.window_add_particle.destroy()
            self.update_particles_listbox()

            self.isrunning = False

    def delete_particle(self):
        for particle_index in self.listbox_particles.curselection()[::-1]:
            particle = self.particles[particle_index]

            self.canvas.delete(particle.drawing)
            self.canvas.delete(particle.drawing_arrow_vel)
            self.canvas.delete(particle.drawing_arrow_accel)

            self.particles.remove(particle)

        self.update_particles_listbox()

    def prev(self):

        if self.isrunning:
            self.playpause()

        self.timeincrement = -self.timeincrement
        self.advance()
        self.timeincrement = -self.timeincrement
        
        self.update_display()

    def playpause(self):
        self.isrunning = not self.isrunning

        if self.isrunning:
            self.button_playpause.config(text=u"\u275A" + u"\u275A")
        else:
            self.button_playpause.config(text=u"\u25B6")

    def stop(self):
        if self.isrunning:
            self.playpause()
        self.start_simulation()

    def next(self):
        if self.isrunning:
            self.playpause()
            
        self.advance()
        self.update_display()

    def update(self):
        self.update_forces()

        if self.isrunning:
            self.advance()
            
        self.update_display()

        self.after(1000/self.targetfps + 1, self.update)

    def update_forces(self):

        for particle in self.particles:
            particle.net_force = [0,0]

            # add up the forces on this particle from each other particle
            for particle2 in self.particles:
                if particle2 != particle:

                    displacement = [particle2.pos[0] - particle.pos[0], particle2.pos[1] - particle.pos[1]]
                    distance = pow(pow(displacement[0], 2) + pow(displacement[1], 2), 0.5)

                    # Newton's law of gravitation: F = Gm1m2/r2
                    # give the distance a minimum value so that the force doesn't get unrealistically large
                    
                    force_mag = self.gravity * particle.mass * particle2.mass
                    force_mag /= max(pow(distance, 2), pow(self.scale * self.bounds_radius, 2))

                    force_dir = math.atan2(displacement[1], displacement[0])
                    force_x = force_mag * math.cos(force_dir)
                    force_y = force_mag * math.sin(force_dir)

                    particle.net_force[0] += force_x
                    particle.net_force[1] += force_y

        for particle in self.particles:
            particle.accel = [0,0]

            # iterate over each axis (x and y)
            for a in [0, 1]:

                # Newton's second law: a = F/m
                particle.accel[a] = particle.net_force[a] / (particle.mass + 0.0)

    def update_display (self):
        for particle in self.particles:
            
            offset = self.particle_avgradius * particle.mass / self.avgmass
            newpos = [int(particle.pos[0] / self.scale + self.bounds_radius),
                      int(particle.pos[1] / self.scale + self.bounds_radius)]
            self.canvas.coords(particle.drawing, newpos[0] - offset, newpos[1] - offset, newpos[0] + offset, newpos[1] + offset)
            
            vel_direction = math.atan2(particle.vel[1], particle.vel[0])
            self.canvas.coords(particle.drawing_arrow_vel, newpos[0], newpos[1],
                               newpos[0] + 30 * math.cos(vel_direction),
                               newpos[1] + 30 * math.sin(vel_direction)
                               )

            accel_direction = math.atan2(particle.accel[1], particle.accel[0])
            self.canvas.coords(particle.drawing_arrow_accel, newpos[0], newpos[1],
                               newpos[0] + 30 * math.cos(accel_direction),
                               newpos[1] + 30 * math.sin(accel_direction)
                               )
            
            if self.particles.index(particle) in self.listbox_particles.curselection():
                self.canvas.itemconfig(particle.drawing, fill="#CCCCCC")
            else:
                self.canvas.itemconfig(particle.drawing, fill="#FFFFFF")

        self.label_time.config(text = "Time: {:.2f} s".format(self.time))

    def advance(self):
        for particle in self.particles:
            for a in [0, 1]:

                # motion formulas: r = r0 + v0t + at2/2, v = v0 + at
                particle.pos[a] += particle.vel[a] * self.timeincrement + particle.accel[a] * self.timeincrement * self.timeincrement / 2.0
                particle.vel[a] += particle.accel[a] * self.timeincrement

                # bounce off the edge of the screen
                if particle.pos[a] < -self.bounds_radius * self.scale:
                    particle.pos[a] = -self.bounds_radius * self.scale
                    
                    # make sure to bounce "negatively" if time increment < 0
                    particle.vel[a] = math.copysign(particle.vel[a], self.timeincrement)

                elif particle.pos[a] > self.bounds_radius * self.scale:
                    particle.pos[a] = self.bounds_radius * self.scale
                    particle.vel[a] = -math.copysign(particle.vel[a], self.timeincrement)

        self.time += self.timeincrement

    def update_particles_listbox(self):
        self.listbox_particles.delete(0, tk.END)

        for particle in self.particles:
            self.listbox_particles.insert(tk.END, repr(particle))

if __name__ == "__main__":
    App().mainloop()
